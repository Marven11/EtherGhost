{
  description = "Application packaged using poetry2nix";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable-small";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python3Packages;
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      in
      {

        # Shell for app dependencies.
        #
        #     nix develop
        #
        # Use this shell for developing your app.
        devShells.default = pkgs.mkShell {
          buildInputs = [
            (pkgs.poetry.withPlugins (ps: with ps; [ 
              poetry-plugin-shell
            ]))
            pythonPackages.notebook
            pythonPackages.ipython
            pythonPackages.pydantic
            pythonPackages.fastapi
            pythonPackages.requests
            pythonPackages.pycryptodome
            pythonPackages.sqlalchemy
            pythonPackages.uvicorn
            pythonPackages.sqlalchemy-utils
            pythonPackages.httpx
            pythonPackages.chardet
          ];
          shellHook = ''
            poetry install
            poetry shell
          '';
        };

        packages.default = with pkgs.python313Packages;
          buildPythonPackage rec {
            pname = "ether-ghost";
            version = "0.2.0";
            pyproject = true;

            propagatedBuildInputs = [
              build
              packaging
              poetry-core
            ];
            dependencies = [
              pydantic
              fastapi
              requests
              pycryptodome
              sqlalchemy
              uvicorn
              sqlalchemy-utils
              httpx
              socksio
              chardet
              python-multipart
            ];

            src = ./.;
          };
      });
}
