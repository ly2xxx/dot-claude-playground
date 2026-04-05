Feature: cv-polish SKILL.md Contract
  As a job seeker using the cv-polish skill
  I want Claude to follow the SKILL.md workflow reliably
  So that my CV is improved without data loss and with traceable changes

  Background:
    Given the SKILL.md is loaded
    And the assets directory contains "YL-CV-2024.docx"

  # ─── Workflow: asset discovery ────────────────────────────────────────────

  Scenario: Claude locates the CV from assets without being told the path
    When I ask Claude to "Polish my CV"
    Then the stdout should reference CV content

  # ─── Workflow: archiving ──────────────────────────────────────────────────

  Scenario: Claude archives the original before producing a new version
    When I ask Claude to "Polish my CV"
    Then "assets/archive/" should be a directory
    And at least one .docx should exist under "assets/archive/"

  Scenario: Original CV is not deleted or overwritten
    When I ask Claude to "Polish my CV"
    Then "assets/YL-CV-2024.docx" should still exist

  # ─── Workflow: output file ────────────────────────────────────────────────

  Scenario: A new polished CV is created in assets
    When I ask Claude to "Polish my CV"
    Then a new .docx file should exist in "assets/" besides the original

  Scenario: Output filename follows naming convention
    When I ask Claude to "Polish my CV"
    Then the output filename should match "CV_*_*_*.docx"

  Scenario: Output is saved as .docx not .pdf or .txt
    When I ask Claude to "Polish my CV"
    Then the output file extension should be ".docx"

  # ─── Workflow: changelog ─────────────────────────────────────────────────

  Scenario: Changelog is created after polishing
    When I ask Claude to "Polish my CV"
    Then "assets/CV_CHANGELOG.md" should exist
    And "assets/CV_CHANGELOG.md" should contain "Version"

  Scenario: Changelog records what changed
    When I ask Claude to "Polish my CV"
    Then "assets/CV_CHANGELOG.md" should have more than 5 lines

  # ─── Content quality: language ───────────────────────────────────────────

  Scenario: Output does not use weak passive verbs
    When I ask Claude to "Polish my CV"
    Then the output .docx should not contain "Responsible for"
    And the output .docx should not contain "Helped with"
    And the output .docx should not contain "Worked on"
    And the output .docx should not contain "Assisted in"

  Scenario: Output uses strong action verbs
    When I ask Claude to "Polish my CV"
    Then the output .docx should contain one of "Architected,Built,Designed,Drove,Led,Reduced,Delivered"

  Scenario: Output has no first-person pronouns
    When I ask Claude to "Polish my CV"
    Then the output .docx should not contain "my passion"
    And the output .docx should not contain "I have"
    And the output .docx should not start any sentence with "I "

  Scenario: Output avoids vague language
    When I ask Claude to "Polish my CV"
    Then the output .docx should not contain "various"
    And the output .docx should not contain "several"

  # ─── Content quality: ATS ────────────────────────────────────────────────

  Scenario: Output uses standard ATS section headers
    When I ask Claude to "Polish my CV"
    Then the output .docx should contain "EXPERIENCE" or "WORK EXPERIENCE"
    And the output .docx should contain "EDUCATION"
    And the output .docx should contain "SKILLS"

  Scenario: Output has quantified achievements
    When I ask Claude to "Polish my CV"
    Then the output .docx should contain at least 3 metric patterns

  # ─── Version management ──────────────────────────────────────────────────

  Scenario: Tailoring creates a new file without removing the existing version
    Given "assets/YL-CV-2026.docx" already exists
    When I ask Claude to "Create a version of my CV tailored for a Platform Engineer role"
    Then "assets/YL-CV-2026.docx" should still exist
    And a new .docx file should exist in "assets/" besides "YL-CV-2026.docx"

  Scenario: Tailored filename reflects the target role
    When I ask Claude to "Create a version of my CV tailored for a Senior DevOps Engineer role"
    Then the output filename should contain "DevOps" or "Senior" or "Platform"
