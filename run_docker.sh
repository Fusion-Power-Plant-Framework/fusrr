docker run -d \
  --name=blender \
  --security-opt seccomp=unconfined `#optional` \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Etc/UTC \
  -e SUBFOLDER=/ `#optional` \
  --env DISPLAY=unix$DISPLAY --privileged \
  -p 3000:3000 \
  -p 3001:3001 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /path/to/config:/config \
  --restart unless-stopped \
  fusrr:latest
