#!/usr/bin/env bash
# nat-map.sh - apply DNAT rules from mappings.csv
# Usage:
#   ./nat-map.sh --dry-run    # just show iptables commands
#   ./nat-map.sh --apply      # apply rules
#   ./nat-map.sh --flush      # remove rules created by this script (careful)
#
OUTER_IF="vmbr0"   # adjust to your external interface on AIGARDEN02
PUB_IP="51.91.105.16"
MAPPINGS="${1:-mappings.csv}"
MODE="dry"
shift 1 || true
for arg in "$@"; do
  case $arg in
    --apply) MODE="apply";;
    --dry-run) MODE="dry";;
    --flush) MODE="flush";;
  esac
done

if [ ! -f "$MAPPINGS" ]; then
  echo "Mappings file not found: $MAPPINGS"
  exit 1
fi

# tag chain/rules with comment "OWALAI-AI360"
apply_cmd() {
  echo "+ $*"
  if [ "$MODE" = "apply" ]; then
    eval "$@"
  fi
}

if [ "$MODE" = "flush" ]; then
  echo "Flushing rules added by this script (searching by comment OWALAI-AI360)..."
  # flush NAT PREROUTING rules with comment
  iptables -t nat -S PREROUTING | grep OWALAI-AI360 | while read -r line; do
    rule=$(echo "$line" | sed 's/^-A/A/')
    echo "Deleting: $rule"
    iptables -t nat $rule
  done
  # flush forward rules with comment
  iptables -S FORWARD | grep OWALAI-AI360 | while read -r line; do
    rule=$(echo "$line" | sed 's/^-A/A/')
    echo "Deleting: $rule"
    iptables $rule
  done
  exit 0
fi

echo "Mode: $MODE"
while IFS=, read -r sub proto ext_port dest_ip dest_port; do
  # skip header or empty
  if [ "$sub" = "subdomain" ] || [ -z "$sub" ]; then
    continue
  fi
  proto_lc=$(echo "$proto" | tr '[:upper:]' '[:lower:]')
  if [ "$proto_lc" != "tcp" ] && [ "$proto_lc" != "udp" ]; then
    proto_lc="tcp"
  fi
  # DNAT rule
  cmd="iptables -t nat -A PREROUTING -d ${PUB_IP}/32 -i ${OUTER_IF} -p ${proto_lc} --dport ${ext_port} -m comment --comment 'OWALAI-AI360' -j DNAT --to-destination ${dest_ip}:${dest_port}"
  apply_cmd "$cmd"
  # FORWARD rule
  cmd2="iptables -A FORWARD -p ${proto_lc} -d ${dest_ip} --dport ${dest_port} -m conntrack --ctstate NEW,ESTABLISHED,RELATED -m comment --comment 'OWALAI-AI360' -j ACCEPT"
  apply_cmd "$cmd2"
done < <(tail -n +2 "$MAPPINGS" | sed 's/\r//g')

echo "Done. If applied, list NAT PREROUTING rules:"
iptables -t nat -L PREROUTING -n --line-numbers | sed -n '1,200p'
