docker-slim --report off build \
--show-clogs \
--http-probe=false \
--continue-after 5 \
--volume ~/.kube/portal/portal-newtest-temp.config:.kube/config \
--include-path "/usr/local/lib/python3.7/site-packages/certifi" \
  mm/netscaler