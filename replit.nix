{pkgs}: {
  deps = [
    pkgs.xclip
    pkgs.mtdev
    pkgs.pkg-config
    pkgs.glib
    pkgs.xorg.libxcb
    pkgs.xorg.libXcursor
    pkgs.xorg.libXrandr
    pkgs.xorg.libXi
    pkgs.xorg.libXinerama
    pkgs.xorg.libXrender
    pkgs.xorg.libXext
    pkgs.xorg.libX11
    pkgs.libGL
    pkgs.mesa
    pkgs.SDL2_ttf
    pkgs.SDL2_mixer
    pkgs.SDL2_image
    pkgs.SDL2
  ];
}
