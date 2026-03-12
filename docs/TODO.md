## Roadmap
- add Docker container to docker hub + repo dockerfile
  <!-- - add docker hub (dh) -->
  <!-- - add docker to github wf -->
  <!-- - setup (Cleanup old Docker Hub tags) in gh wf -->
  - add dh to readme
  - add docs to dockerhub
  
- Add configuration command (read alias and add extra)
    <!-- 1. show creads - for curent profile -->
       <!-- 1. update config with ne utils -->
       <!-- 2. Session Token:     [Active] make it not hard-coded -->
    <!-- 2. Verify 
       1. modify with utils    -->
    <!-- 3. configure -  -->
       <!-- 1. change all configs +  -->
       <!-- 2. creds -->
    4. Add Upgrade app
       1. need test if it's work
    5. ecr 
       <!-- 1. login -->
       <!-- 2. purge -->
       <!-- 3. login public -->
       <!-- 4. test all ecr command -->
       1. add to docs
    6. docs
   
- Add documentation

- Add Windows support
  
- Session caching (Not apply mfa each time)

- Auto-refresh role (same as aws-vault)

- Pipe-friendly output

- TUI mode

- JSON output mode
  `awscli-addons whoami --json`

- SSO support




docker build -t awscli-addons .

# Example: Check whoami (mounting your local AWS credentials)
docker run --rm -v ~/.aws:/root/.aws awscli-addons whoami
docker run --rm  -it awscli-addons bash
VERSION=feature/init tools/installer.sh