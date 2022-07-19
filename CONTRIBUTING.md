# Contributing
i8 Terminal is open source, everyone is free to contribute.
But please follow the guidelines below.

## Guidelines
### Branching Conventions
We use the git flow convention: `feature/<small-description>`.

### Reviewing
All changes (not matter how minor) to main are made through Pull Requests (PRs).
All PRs are reviewed by at least one reviewer.
If you know that someone may have an opinion on your change, make sure this person reviewed your code before merging.

### Communication
We use [Slack](https://investor8.slack.com/signup) for communication.

## How to contribute

The preferred workflow for contributing to i8 Terminal is to clone the
[GitHub repository](https://github.com/investoreight/i8-terminal), develop on a branch and make a Pull Request.

Steps:

  1. Create an issue of what you are going to do at [https://github.com/investoreight/i8-terminal/issues](https://github.com/investoreight/i8-terminal/issues).

  2. Fork the Project

  3. Create a ``feature`` branch to hold your development changes:

     ```bash
     $ git checkout -b {feature|fix}/<feature-name>
     ```

     Always use a ``feature`` branch. It's good practice to never work on the ``main`` branch!

  4. Install the pre-commit hooks by running: pre-commit install. Any time you commit a change, linters will be run automatically. On changes, you will have to re-commit.

  5. Develop the feature on your feature branch.

  6. Add changed files using ``git add`` and then ``git commit`` files:

     ```bash
     $ git add modified_files
     $ git commit
     ```
     to record your changes in Git, then push the changes to your GitHub account with:

     ```bash
     $ git push -u origin {feature|fix}/<feature-name>
     ```

       * **Be descriptive in your commit messages. Start with a verb in the present tense.**
       * **Group commit changes that belong together.**

  7. Browse to [https://github.com/investoreight/i8-terminal](https://github.com/investoreight/i8-terminal) and follow instructions to create Pull Request.
     Make sure you add reviewers to your PR. Your code should be reviewed by at least 1 person and by everyone in the wider contributing team you know could have an opinion on your change.

  8. Optionally use [Slack](https://investor8.slack.com/signup) to advertise your PR.

(If any of the above seems like magic to you, please look up the
[Git documentation](https://git-scm.com/documentation) on the web, or ask a friend or another contributor for help.)