# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-02-16

### Added

- Architecture reference (ARCHITECTURE.md): 8 design principles, dependency
  graph, interfaces, build order, high-level architecture, scoring model,
  verification approach, and open questions.
- Engineering standards (STANDARDS.md): 14 cross-cutting standards covering
  naming, configuration, versioning, logging, error handling, observability,
  testing, security, CI/CD, documentation, dependencies, and code style.
- 18 ADRs (0001-0018) establishing foundational decisions: language choice,
  SDL design, schema format, polyrepo structure, event format, provider
  abstraction, licensing, observability, branching, code style, versioning,
  governance process, and more.
- ADR and RFC templates (adrs/TEMPLATE.md, rfcs/TEMPLATE.md).
- Compatibility matrix placeholder (COMPATIBILITY.md).
- 20 repo bootstrap templates (templates/) covering agent instructions,
  CI workflows, pre-commit hooks, toolchain configs, manifests, gitignores,
  changelog, license, markdownlint config, and GitHub issue/PR templates.
- GitHub Actions CI for governance repo (markdownlint via pre-commit).
- GitHub issue templates (ADR proposal, RFC proposal) and PR template.
