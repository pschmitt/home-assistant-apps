# Agent notes

This repository contains Home Assistant apps and add-ons. Each add-on's own
README and workflow define its build and configuration.

- Keep changes scoped to the affected add-on and run its existing checks and
  the matching CI workflow.
- Use a test Home Assistant instance for integration checks. Keep credentials,
  private service URLs, and device identifiers out of examples and logs.
- Before changing workflows, check for reusable workflows or actions in
  [ci-workflows](https://github.com/pschmitt/ci-workflows) and preserve
  existing triggers, inputs, permissions, and check coverage.
