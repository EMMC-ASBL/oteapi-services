# Changelog

## [Unreleased](https://github.com/EMMC-ASBL/oteapi-services/tree/HEAD)

[Full Changelog](https://github.com/EMMC-ASBL/oteapi-services/compare/v1.20250410.410...HEAD)

**Merged pull requests:**

- \[pre-commit.ci\] pre-commit autoupdate [\#622](https://github.com/EMMC-ASBL/oteapi-services/pull/622) ([pre-commit-ci[bot]](https://github.com/apps/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [\#616](https://github.com/EMMC-ASBL/oteapi-services/pull/616) ([pre-commit-ci[bot]](https://github.com/apps/pre-commit-ci))

## [v1.20250410.410](https://github.com/EMMC-ASBL/oteapi-services/tree/v1.20250410.410) (2025-04-10)

[Full Changelog](https://github.com/EMMC-ASBL/oteapi-services/compare/v1.20230324.302...v1.20250410.410)

**Implemented enhancements:**

- Upgrade to using `ruff` for linting [\#451](https://github.com/EMMC-ASBL/oteapi-services/issues/451)
- Migrate to pydantic v2 [\#338](https://github.com/EMMC-ASBL/oteapi-services/issues/338)
- Generic triplestore interface & replace SFTP [\#283](https://github.com/EMMC-ASBL/oteapi-services/issues/283)
- Config option for setting `base_url`/`root_url` [\#177](https://github.com/EMMC-ASBL/oteapi-services/issues/177)
- An introspective metadata endpoint [\#113](https://github.com/EMMC-ASBL/oteapi-services/issues/113)
- Separate parse and download [\#55](https://github.com/EMMC-ASBL/oteapi-services/issues/55)
- General documentation and document configuration options [\#10](https://github.com/EMMC-ASBL/oteapi-services/issues/10)

**Fixed bugs:**

- Install `safety` in a separate environment in CI [\#525](https://github.com/EMMC-ASBL/oteapi-services/issues/525)
- OpenAPI is not retrievable [\#447](https://github.com/EMMC-ASBL/oteapi-services/issues/447)
- pre-commit config should be updated to state `master` instead of `main` [\#434](https://github.com/EMMC-ASBL/oteapi-services/issues/434)
- Docker compose failing in CI test workflows [\#370](https://github.com/EMMC-ASBL/oteapi-services/issues/370)

**Closed issues:**

- Fallback to FakeRedis if Redis is not available [\#412](https://github.com/EMMC-ASBL/oteapi-services/issues/412)
- Remove triplestore and sftp  [\#397](https://github.com/EMMC-ASBL/oteapi-services/issues/397)
- Revert update of codecov-action from v4 to v3 [\#325](https://github.com/EMMC-ASBL/oteapi-services/issues/325)
- Add oteapi-dlite-plugin python package as a dependency [\#300](https://github.com/EMMC-ASBL/oteapi-services/issues/300)
- Remove sftp service from production compose file [\#120](https://github.com/EMMC-ASBL/oteapi-services/issues/120)
- Issue with TripleStoreConfig on latest oteapi image  [\#112](https://github.com/EMMC-ASBL/oteapi-services/issues/112)

**Merged pull requests:**

- \[Auto-generated\] Update dependencies [\#459](https://github.com/EMMC-ASBL/oteapi-services/pull/459) ([TEAM4-0](https://github.com/TEAM4-0))
- \[Auto-generated\] Update dependencies [\#452](https://github.com/EMMC-ASBL/oteapi-services/pull/452) ([TEAM4-0](https://github.com/TEAM4-0))
- \[Auto-generated\] Update dependencies [\#429](https://github.com/EMMC-ASBL/oteapi-services/pull/429) ([TEAM4-0](https://github.com/TEAM4-0))

## [v1.20230324.302](https://github.com/EMMC-ASBL/oteapi-services/tree/v1.20230324.302) (2023-03-24)

[Full Changelog](https://github.com/EMMC-ASBL/oteapi-services/compare/beaeac12453922f381a676df7876427fa62677fe...v1.20230324.302)

**Implemented enhancements:**

- Authentication pathway [\#178](https://github.com/EMMC-ASBL/oteapi-services/issues/178)
- Implement Function router [\#92](https://github.com/EMMC-ASBL/oteapi-services/issues/92)
- Support local paths for plugins in container-image [\#77](https://github.com/EMMC-ASBL/oteapi-services/issues/77)
- Specify local plugin versions to install [\#76](https://github.com/EMMC-ASBL/oteapi-services/issues/76)
- Implement way to provide list of plugin repositories [\#72](https://github.com/EMMC-ASBL/oteapi-services/issues/72)
- Allow custom path to `oteapi-core` in `development` Docker target [\#66](https://github.com/EMMC-ASBL/oteapi-services/issues/66)
- Data resource prioritization [\#56](https://github.com/EMMC-ASBL/oteapi-services/issues/56)
- Update to oteapi-core v0.1.0 [\#51](https://github.com/EMMC-ASBL/oteapi-services/issues/51)
- Handle new `SessionUpdate` response from strategy methods [\#47](https://github.com/EMMC-ASBL/oteapi-services/issues/47)
- Consider replacing dependabot with a custom workflow [\#38](https://github.com/EMMC-ASBL/oteapi-services/issues/38)
- Move over `docker-compose.yml` from oteapi-deploy [\#18](https://github.com/EMMC-ASBL/oteapi-services/issues/18)
- Use official release line for oteapi-core [\#17](https://github.com/EMMC-ASBL/oteapi-services/issues/17)
- Use pydantic models as Response Model [\#9](https://github.com/EMMC-ASBL/oteapi-services/issues/9)
- Implement dependabot [\#8](https://github.com/EMMC-ASBL/oteapi-services/issues/8)

**Fixed bugs:**

- Have correct version number in OpenAPI schema [\#234](https://github.com/EMMC-ASBL/oteapi-services/issues/234)
- Pylint fails with useless-option-value / R0022 [\#182](https://github.com/EMMC-ASBL/oteapi-services/issues/182)
- Implement sanity checks for updating the `requirements.txt` file [\#159](https://github.com/EMMC-ASBL/oteapi-services/issues/159)
- Clarify how to install local `oteapi-core` for plugin development [\#82](https://github.com/EMMC-ASBL/oteapi-services/issues/82)
- Custom pydantic types not used for `.construct()` method [\#67](https://github.com/EMMC-ASBL/oteapi-services/issues/67)
- CI automerge - GH GraphQL type update [\#58](https://github.com/EMMC-ASBL/oteapi-services/issues/58)
- Typo issue with CI workflow [\#50](https://github.com/EMMC-ASBL/oteapi-services/issues/50)
- Calls to `parse` method for parse strategies should be `get` [\#41](https://github.com/EMMC-ASBL/oteapi-services/issues/41)
- Update according to new `oteapi-core` plugins API [\#36](https://github.com/EMMC-ASBL/oteapi-services/issues/36)
- Out-of-scope CVE from NumPy makes safety cry [\#20](https://github.com/EMMC-ASBL/oteapi-services/issues/20)
- Update tests to new structure [\#3](https://github.com/EMMC-ASBL/oteapi-services/issues/3)
- Use the `get()` method throughout for strategies [\#42](https://github.com/EMMC-ASBL/oteapi-services/pull/42) ([CasperWA](https://github.com/CasperWA))

**Closed issues:**

- `set-output` is deprecated for GH Actions [\#233](https://github.com/EMMC-ASBL/oteapi-services/issues/233)
- deprecate run\(\) method for transformation strategies [\#226](https://github.com/EMMC-ASBL/oteapi-services/issues/226)
- Development image does not start correctly [\#89](https://github.com/EMMC-ASBL/oteapi-services/issues/89)
- Add a triple store to the docker-compose for mapping strategy [\#75](https://github.com/EMMC-ASBL/oteapi-services/issues/75)
- Remove checkboxes from PR body for the "update `requirements.txt`" workflow [\#60](https://github.com/EMMC-ASBL/oteapi-services/issues/60)
- Clean up dockerfile [\#30](https://github.com/EMMC-ASBL/oteapi-services/issues/30)
- Update README with correct env vars [\#12](https://github.com/EMMC-ASBL/oteapi-services/issues/12)
- Maybe publish Docker image on GitHub Packages [\#11](https://github.com/EMMC-ASBL/oteapi-services/issues/11)
- Rename endpoint "datasource" to "dataresource" for consistency [\#5](https://github.com/EMMC-ASBL/oteapi-services/issues/5)
- Implement CI/CD test for the `development` target build of Dockerfile [\#4](https://github.com/EMMC-ASBL/oteapi-services/issues/4)
- Update requirements to new oteapi-core [\#1](https://github.com/EMMC-ASBL/oteapi-services/issues/1)

**Merged pull requests:**

- Enh/add auth [\#189](https://github.com/EMMC-ASBL/oteapi-services/pull/189) ([MBueschelberger](https://github.com/MBueschelberger))
- \[Auto-generated\] Update dependencies [\#122](https://github.com/EMMC-ASBL/oteapi-services/pull/122) ([TEAM4-0](https://github.com/TEAM4-0))
- \[Auto-generated\] Update dependencies [\#119](https://github.com/EMMC-ASBL/oteapi-services/pull/119) ([TEAM4-0](https://github.com/TEAM4-0))
- \[Auto-generated\] Update dependencies [\#117](https://github.com/EMMC-ASBL/oteapi-services/pull/117) ([TEAM4-0](https://github.com/TEAM4-0))
- \[Auto-generated\] Update dependencies [\#115](https://github.com/EMMC-ASBL/oteapi-services/pull/115) ([TEAM4-0](https://github.com/TEAM4-0))
- \[Auto-generated\] Update dependencies [\#111](https://github.com/EMMC-ASBL/oteapi-services/pull/111) ([TEAM4-0](https://github.com/TEAM4-0))
- \[Auto-generated\] Update dependencies [\#106](https://github.com/EMMC-ASBL/oteapi-services/pull/106) ([TEAM4-0](https://github.com/TEAM4-0))
- Added pull request template [\#102](https://github.com/EMMC-ASBL/oteapi-services/pull/102) ([francescalb](https://github.com/francescalb))
- \[Auto-generated\] Update dependencies [\#101](https://github.com/EMMC-ASBL/oteapi-services/pull/101) ([TEAM4-0](https://github.com/TEAM4-0))
- Update README.md [\#99](https://github.com/EMMC-ASBL/oteapi-services/pull/99) ([quaat](https://github.com/quaat))
- Trj/75 add a triplestore and sample endpoint [\#97](https://github.com/EMMC-ASBL/oteapi-services/pull/97) ([Treesarj](https://github.com/Treesarj))
- Check for downloadUrl/mediaType before access\* [\#95](https://github.com/EMMC-ASBL/oteapi-services/pull/95) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#94](https://github.com/EMMC-ASBL/oteapi-services/pull/94) ([TEAM4-0](https://github.com/TEAM4-0))
- Implement `/function` endpoint and router [\#93](https://github.com/EMMC-ASBL/oteapi-services/pull/93) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#88](https://github.com/EMMC-ASBL/oteapi-services/pull/88) ([TEAM4-0](https://github.com/TEAM4-0))
- Correct handling of arguments to entrypoint that contain spaces. [\#85](https://github.com/EMMC-ASBL/oteapi-services/pull/85) ([jesper-friis](https://github.com/jesper-friis))
- Use pipe \(`|`\) instead of colon \(`:`\) for plugins [\#84](https://github.com/EMMC-ASBL/oteapi-services/pull/84) ([CasperWA](https://github.com/CasperWA))
- Clarify docker compose file for plugin developers [\#83](https://github.com/EMMC-ASBL/oteapi-services/pull/83) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#80](https://github.com/EMMC-ASBL/oteapi-services/pull/80) ([TEAM4-0](https://github.com/TEAM4-0))
- New plugin package delimiter: A colon \(`:`\) [\#78](https://github.com/EMMC-ASBL/oteapi-services/pull/78) ([CasperWA](https://github.com/CasperWA))
- Use an entrypoint script for the Dockerfile [\#73](https://github.com/EMMC-ASBL/oteapi-services/pull/73) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#70](https://github.com/EMMC-ASBL/oteapi-services/pull/70) ([TEAM4-0](https://github.com/TEAM4-0))
- Remove usage of `.construct()` method [\#68](https://github.com/EMMC-ASBL/oteapi-services/pull/68) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#65](https://github.com/EMMC-ASBL/oteapi-services/pull/65) ([TEAM4-0](https://github.com/TEAM4-0))
- \[Auto-generated\] Update dependencies [\#63](https://github.com/EMMC-ASBL/oteapi-services/pull/63) ([TEAM4-0](https://github.com/TEAM4-0))
- Remove checkboxes from `requirements.txt` update PR body [\#62](https://github.com/EMMC-ASBL/oteapi-services/pull/62) ([CasperWA](https://github.com/CasperWA))
- Fix type notation for GH GraphQL [\#59](https://github.com/EMMC-ASBL/oteapi-services/pull/59) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#54](https://github.com/EMMC-ASBL/oteapi-services/pull/54) ([TEAM4-0](https://github.com/TEAM4-0))
- Add missing `==` operator to CI workflow [\#53](https://github.com/EMMC-ASBL/oteapi-services/pull/53) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#48](https://github.com/EMMC-ASBL/oteapi-services/pull/48) ([TEAM4-0](https://github.com/TEAM4-0))
- Bumped required version of oteapi-core up to 0.0.6 [\#46](https://github.com/EMMC-ASBL/oteapi-services/pull/46) ([jesper-friis](https://github.com/jesper-friis))
- Pydantic response models [\#44](https://github.com/EMMC-ASBL/oteapi-services/pull/44) ([CasperWA](https://github.com/CasperWA))
- Add new workflow CD publish job [\#43](https://github.com/EMMC-ASBL/oteapi-services/pull/43) ([CasperWA](https://github.com/CasperWA))
- Improve dependency updates [\#40](https://github.com/EMMC-ASBL/oteapi-services/pull/40) ([CasperWA](https://github.com/CasperWA))
- Update code to be compliant with `oteapi-core` v0.0.5 [\#39](https://github.com/EMMC-ASBL/oteapi-services/pull/39) ([CasperWA](https://github.com/CasperWA))
- Use oteapi-core v0.0.4 [\#37](https://github.com/EMMC-ASBL/oteapi-services/pull/37) ([CasperWA](https://github.com/CasperWA))
- Update Dockerfile - use python base image [\#32](https://github.com/EMMC-ASBL/oteapi-services/pull/32) ([CasperWA](https://github.com/CasperWA))
- \[Auto-generated\] Update dependencies [\#29](https://github.com/EMMC-ASBL/oteapi-services/pull/29) ([TEAM4-0](https://github.com/TEAM4-0))
- Ignore ID 44715 for safety [\#21](https://github.com/EMMC-ASBL/oteapi-services/pull/21) ([CasperWA](https://github.com/CasperWA))
- Add Docker Compose template/example [\#19](https://github.com/EMMC-ASBL/oteapi-services/pull/19) ([CasperWA](https://github.com/CasperWA))
- Implement dependabot [\#16](https://github.com/EMMC-ASBL/oteapi-services/pull/16) ([CasperWA](https://github.com/CasperWA))
- Update README \(for env vars\) [\#15](https://github.com/EMMC-ASBL/oteapi-services/pull/15) ([CasperWA](https://github.com/CasperWA))
- Test Dockerfile in CI/CD [\#7](https://github.com/EMMC-ASBL/oteapi-services/pull/7) ([CasperWA](https://github.com/CasperWA))
- Got the services up and running  [\#6](https://github.com/EMMC-ASBL/oteapi-services/pull/6) ([jesper-friis](https://github.com/jesper-friis))
- Flb/close1 fix to oteapicore on asbl [\#2](https://github.com/EMMC-ASBL/oteapi-services/pull/2) ([francescalb](https://github.com/francescalb))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
