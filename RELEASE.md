# Release Checklist

- [ ] Create new branch `release/x.y.z`
- [ ] Update CHANGELOG.md and commit changes
- [ ] Update version in `setup.py` to match release and commit changes
- [ ] Open PR with title "Release X.Y.Z" and ensure tests pass
- [ ] Once tests have passed, merge PR
- [ ] Pull master and create tag `git tag -a x.y.z -m "vX.Y.Z"`
- [ ] `git push --tags`
- [ ] Wait for and ensure that release build succeeds and publishes new package to https://pypi.org

