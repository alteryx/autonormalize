# Release Process

## 0. Pre-Release Checklist

Before starting the release process, verify the following:

* All work required for this release has been completed and the team is ready to release.
* Get agreement on the version number to use for the release.

### Version Numbering

Autonormalize uses [semantic versioning](https://semver.org/). Every release has a major, minor and patch version number, and are displayed like so: `<majorVersion>.<minorVersion>.<patchVersion>`.

## 1. Create Autonormalize release on Github

### Create release branch

1. Branch off of AutoNormalize `main`. For the branch name, please use "release_vX.Y.Z" as the naming scheme (e.g. "release_v1.0.1").

### Bump version number

1. Bump `__version__` in `setup.py`, `autonormalize/__init__.py`, and `woodwork/tests/test_version.py`.

### Update Release Notes

1. Replace "Future Release" in `docs/source/release_notes.rst` with the current date

    ```markdown
    v1.0.1 Dec 3, 2021
    ====================
    ```

2. Remove any unused Release Notes sections for this release (e.g. Fixes, Testing Changes)
3. Add yourself to the list of contributors to this release and **put the contributors in alphabetical order**
4. The release PR does not need to be mentioned in the list of changes
5. Add a commented out "Future Release" section with all of the Release Notes sections above the current section

    ```markdown
    .. Future Release
      ==============
        * Enhancements
        * Fixes
        * Changes
        * Documentation Changes
        * Testing Changes

    .. Thanks to the following people for contributing to this release:
    ```

An example can be found here: <https://github.com/alteryx/autonormalize/pull/TODO:EDIT THIS >

Checklist before merging:

* PR has been reviewed and approved.
* Confirm with the team that `main` will be frozen until step 2 (Github Release) is complete.

## 2. Create Github Release

After the release pull request has been merged into the `main` branch, it is time draft the github release. [Example release](https://github.com/alteryx/autonormalize/releases/tag/v1.0.1)

* The target should be the `main` branch
* The tag should be the version number with a v prefix (e.g. v1.0.1)
* Release title is the same as the tag
* Release description should be the full Release Notes updates for the release, including the line thanking contributors.  Contributors should also have their links changed from the docs syntax (:user:\`tuethan1999\`) to github syntax (@tuethan1999)
* This is not a pre-release
