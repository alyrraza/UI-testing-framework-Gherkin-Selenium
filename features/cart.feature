@cart
Feature: Shopping Cart on SauceDemo
  As a logged in user
  I want to add and remove items from cart
  So that I can manage my shopping

  Background:
    Given I am logged in as "standard_user"

  @smoke @happy_path
  Scenario: Add single item to cart
    When I add "Sauce Labs Backpack" to the cart
    Then the cart count should be "1"

  @happy_path
  Scenario: Add multiple items to cart
    When I add "Sauce Labs Backpack" to the cart
    And I add "Sauce Labs Bike Light" to the cart
    Then the cart count should be "2"

  @happy_path
  Scenario: Remove item from cart
    When I add "Sauce Labs Backpack" to the cart
    And I remove "Sauce Labs Backpack" from the cart
    Then the cart count should be "0"

  @happy_path
  Scenario: View cart contents
    When I add "Sauce Labs Backpack" to the cart
    And I navigate to the cart
    Then I should see "Sauce Labs Backpack" in the cart