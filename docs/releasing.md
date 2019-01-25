1. Increment version number in `getmac/getmac.py`
2. Update CHANGELOG header from UNRELEASED to the version and add the date
3. Run static analysis checks (`tox -e check`)
4. Run the test suite on the main supported platforms (`tox`)
    a) Windows
    b) Ubuntu
    c) CentOS
    d) OSX
5. Clean the environment
    a) Windows: `scripts\clean.ps1`
    b) Bash: `bash ./scripts/clean.sh`
6. `python setup.py sdist bdist_wheel`
7. `twine upload dist/*`
8. Create a tagged release on GitHub including:
    a) The relevant section of the CHANGELOG in the body
    b) The source and binary wheels
9. Edit the package name in setup.py to `get-mac`, and re-run
steps 5 and 6, since people apparently don't check their
dependencies and ignore runtime warnings.
10. Announce the release in the normal places