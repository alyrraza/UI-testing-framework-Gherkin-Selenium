@login
Feature: User Authentication on SauceDemo
  As a registered user
  I want to log in and log out of SauceDemo
  So that I can access my account securely

  Background:
    Given I am on the SauceDemo login page

  @smoke @happy_path
  Scenario: Successful login with valid credentials
    When I enter username "standard_user" and password "secret_sauce"
    And I click the login button
    Then I should be on the inventory page
    And the page title should be "Products"

  @unhappy_path
  Scenario: Login fails with invalid password
    When I enter username "standard_user" and password "wrong_password"
    And I click the login button
    Then I should see an error message containing "Username and password do not match"

  @unhappy_path
  Scenario: Login fails for locked out user
    When I enter username "locked_out_user" and password "secret_sauce"
    And I click the login button
    Then I should see an error message containing "Sorry, this user has been locked out"

  @unhappy_path
  Scenario: Login fails with empty credentials
    When I enter username "" and password ""
    And I click the login button
    Then I should see an error message containing "Username is required"

  @smoke @logout
  Scenario: Successful logout after login
    When I enter username "standard_user" and password "secret_sauce"
    And I click the login button
    Then I should be on the inventory page
    When I open the burger menu and click logout
    Then I should be on the login page

  @data_driven
  Scenario Outline: Data-driven login with multiple credentials
    When I enter username "<username>" and password "<password>"
    And I click the login button
    Then the login result should be "<expected_result>"

    Examples:
      | username          | password     | expected_result |
      | standard_user     | secret_sauce | success         |
      | locked_out_user   | secret_sauce | failure         |
      | standard_user     | wrong_pass   | failure         |
      | non_existent_user | secret_sauce | failure         |