@checkout
Feature: Checkout Process on SauceDemo
  As a logged in user
  I want to complete the checkout process
  So that I can purchase items

  Background:
    Given I am logged in as "standard_user"

  @smoke @happy_path
  Scenario: Complete checkout successfully
    When I add "Sauce Labs Backpack" to the cart
    And I navigate to the cart
    And I click checkout
    And I enter first name "Ali" last name "Raza" zip "12345"
    And I click continue
    Then I should see the order summary
    When I click finish
    Then I should see "Thank you for your order!"

  @unhappy_path
  Scenario: Checkout fails with empty first name
    When I add "Sauce Labs Backpack" to the cart
    And I navigate to the cart
    And I click checkout
    And I enter first name "" last name "Raza" zip "12345"
    And I click continue
    Then I should see an error "First Name is required"

  @unhappy_path
  Scenario: Checkout fails with empty zip code
    When I add "Sauce Labs Backpack" to the cart
    And I navigate to the cart
    And I click checkout
    And I enter first name "Ali" last name "Raza" zip ""
    And I click continue
    Then I should see an error "Postal Code is required"