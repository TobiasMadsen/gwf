.. _formaintainers:

===============
For Maintainers
===============

The *gwf* build, testing and deployment process is automated through Travis
with some safety measures provided by GitHub.

The ``master`` branch is protected and changes can not be pushed directly to this
branch. The requirements for merging a feature branch into ``master`` are:

1. All changes must be made on feature branches and then merged into `master`
   when the tests pass.
2. The feature branch must be completely up to date with `master` before merging.

This ensures that ``master`` is reasonably stable. Before major changes are merged
into ``master`` they should be discussed and reviewed via a PR.

Merging Changes
===============

1. Make sure that the changes have proper test coverage, e.g. by checking the branch
   on `Coveralls <https://coveralls.io/github/gwforg/gwf>`_.

2. Check that the PR includes necessary updates of ``CHANGELOG.rst`` and ``CONTRIBUTORS.rst``.

3. Always make a merge commit (don't rebase/fast-forward). The merge commit will be
   referenced in the change log.

4. Add the change to the change log for the coming (draft) release on
   `GitHub <https://github.com/gwforg/gwf/releases>`_. Make sure to follow the
   formatting used in previous change logs. Also, read about
   `how to keep a change log <http://keepachangelog.com/en/0.3.0/>`_.

Rolling a New Release
=====================

1. Make sure that all changes for the new release have been merged into ``master``
   and that tests pass. Check `Travis <https://travis-ci.org/mailund/gwf>`_.

2. Create a new branch for the release, named ``release-vX.X.X``.

3. In the release branch, increase the version number in ``gwf/__init__.py``.

4. Make any other release-related changes such as adding new contributors to
   ``CONTRIBUTORS.rst`` or adding missing items to ``CHANGELOG.rst``.

5. Commit the changes and push the branch. Wait for tests to run.

6. Open a `pull request <https://github.com/gwforg/gwf/pulls>`_ for the release.
   Request a reviewer for the PR and wait for comments.

7. Merge the PR into master when everyone's happy. Wait for tests to run.

8. Make a new release by tagging the merge commit with the version number, e.g.
   ``vX.X.X``. Push the tag and wait for Travis to catch up.

9. Pop a bottle of champagne!

Creating the release on GitHub will automatically run all tests (again),
build a source and wheel package and deploy them to PyPI, and build a Conda
package and deploy it to the `gwforg` channel on `Anaconda.org`. The documentation
will be automatically be built by `ReadTheDocs`.
