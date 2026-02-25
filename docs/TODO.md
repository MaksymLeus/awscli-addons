- install.sh
  <!-- 1. configure correct setup -->
  <!-- 2. test it -->
  3. write docs
  <!-- 4. ADD awscli-aliases  -->

- github action workflow
  <!-- 1. Create setup  -->
  <!-- 2. test in tempo repo -->
  <!-- 3. Write docs -->

add Docker container to docker hub + repo dockerfile

- python app
  1. Add configuration command
     <!-- 1. if don;t exist aws-cli -->
     <!-- 2. to simplify setup of work station -->
     1. Add commands
        1. show creads - for curent profile
        2. configure - change all configs + creds
        3. Add Upgrade app
        4. login ecr https://github.com/lamhaison/aws-cli-utils/blob/main/services/ecr.sh
     2. add docs
  2. Add Windows support




## Roadmap
- SSO support
- Session caching (Not apply mfa each time)
- Auto-refresh role (same as aws-vault)
- Pipe-friendly output
- TUI mode
- JSON output mode
  `awscli-addons whoami --json`
- etc


