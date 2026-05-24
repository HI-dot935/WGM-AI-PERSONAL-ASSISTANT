{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.portaudio
    pkgs.espeak
    pkgs.ffmpeg
  ];
}
