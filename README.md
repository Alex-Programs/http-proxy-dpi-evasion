# http-proxy-dpi-evasion
Run HTTP proxy payload inside normal-looking HTTP traffic to a custom relay server. Evades DPIs that see it as legitimate, unencrypted traffic that they are filtering - not noticing the encrypted payload.

I know the code is horrible. I wrote it a year ago focusing on getting a working proof-of-concept. If the need arises to practically use it I'll rewrite it in Rust and make it actually practical. It's currently slow, has no queue scheduler whatsoever, and takes about a minute to load a complex webapp like Discord.
