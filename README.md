# http-proxy-dpi-evasion
Run HTTP proxy payload inside normal-looking HTTP traffic to a custom relay server. Evades DPIs that see it as legitimate, unencrypted traffic that they are filtering - not noticing the encrypted payload.

Currently quite slow, and if you use something that has a lot of requests, they'll be stuck in a huge queue and you won't have internet access till it's done. The bottleneck is in the web server - I'm considering rewriting in Rust to speed it up.

Don't expect it to be particularly reliable, it's a PoC and a backup.
