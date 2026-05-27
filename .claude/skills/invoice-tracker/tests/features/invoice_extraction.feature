Feature: LLM-driven invoice extraction
  As a user with property invoices
  I want the LLM to follow the invoice-tracker skill instructions and extract data to CSV
  So that I can reliably track my costs.

  Scenario Outline: Model extracts correct total and valid CSV
    Given the invoice tracker skill instructions
    And the LLM model is "<model>"
    When the user provides the invoice "1883739.pdf" and asks to process it
    Then the LLM outputs a valid invoices.csv row with total "903.53"
    And the output is evaluated against the skill instructions

    Examples:
      | model        |
      | glm-4.6:cloud       |
