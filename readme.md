# Wild Eldoria — Game Documentation

## Overview

**Wild Eldoria** is a 2D fantasy game developed in **Pygame**. The main objective is to build and upgrade your base, explore the world, gather resources, fight enemies, and progress through increasingly difficult challenges. The game revolves around survival, crafting, combat, and strategic upgrades.

---

## Main Map (Base Map)

The main map is a one‑screen area that serves as the core base of the player. It contains interactive buildings and stations essential for progression.

### Elements on the Main Map

1. **Four buildings**, each with a dedicated interior and unique functionality:

   * **Bedroom**
   * **Smith**
   * **Tailor**
   * **Witch**

2. **Fireplace** — an interactive point where the player can manually produce food.

3. **Exit to the Exploration Map** — located on the left boundary of the screen. Stepping beyond it automatically transitions the view to the larger world map.

---

## Buildings and Their Functions

Each building is a separate interior with its own set of actions.

### Bedroom

* Used to **save the game**.
* May be expanded later with sleeping or regeneration mechanics.

### Smith

* Used to **purchase weapons** and **tools**.
* Tools can be upgraded to improve mining speed and combat efficiency.

### Tailor

* Used to craft and upgrade **armor**.
* Can create additional equipment such as:

  * helmets,
  * chestplates,
  * boots,
  * **larger backpacks** (increase inventory size).

### Witch

* Used to craft **consumable items**, including:

  * healing potions,
  * stat‑boosting potions,
  * single‑use magical items.

---

## Fireplace System

The main map includes a **Fireplace**, where the player can manually craft food.

* Food requires resources from the inventory.
* Crafted food restores health or energy.

---

## Exploration Map (World Map)

The exploration map is a larger area accessed by leaving the main map through the left side.

### Characteristics

* Made of destructible **blocks**.
* The player can **move between blocks** and dig through them using tools.
* Contains **four underground dungeon structures**, each with enemies and rewards.

---

## Underground Structures (Dungeons)

There are four unique dungeon areas throughout the world map.

### Each dungeon contains:

* **Enemies** of varying difficulty.
* **Rewards**, including:

  * gold,
  * resources,
  * rare items,
  * character upgrades.
* A multi‑layered layout requiring exploration.

---

## Currency and Economy

* The main currency is **gold**.
* Gold is obtained by:

  * defeating enemies,
  * exploring dungeons,
  * destroying certain blocks,
  * discovering chests.
* Gold is used for buying weapons, tools, armor, and consumables.

---

## Combat System

* Combat is **real‑time**.
* Weapons purchased from the Smith determine attack speed and damage.
* Different enemies appear on the surface and inside dungeons.

---

## Tools and Resource Gathering

* Tools determine the player’s ability to destroy blocks on the exploration map.
* High‑tier tools allow access to harder materials and faster mining.

---

## Day/Night Cycle

The game includes a dynamic day/night system affecting gameplay.

### Cycle Duration

* A full **day → night → day** cycle lasts **10 minutes of real‑world time**.
* The time of day may influence:

  * enemy spawns,
  * visibility,
  * buffs and debuffs.

### Survival Day Counter

* The game tracks how many days the player survives **without dying**.
* Each completed cycle increments the survival day counter by 1.

### Map Reset

* Every **7 in‑game days**, the exploration map is **reset**.
* Reset includes:

  * regenerating all blocks,
  * respawning enemies,
  * refreshing dungeon rewards.

---

## Interface and Controls

* The main map matches the size of the player’s screen.
* Transition to the exploration map occurs automatically when crossing the left boundary.
* Buildings and crafting stations activate through proximity‑based interaction.

---

## Quest System

Wild Eldoria includes a structured quest system guiding player progression.

### Tutorial Quest

* The game begins with a **mandatory tutorial quest**.
* The tutorial includes:

  * an **introduction text** presenting the world and basic controls,
  * guided steps teaching movement, interaction, crafting, and combat basics,
  * navigation leading the player toward their **first fight**.
* The tutorial must be completed before the player can fully access other game features.

### Weapon Choice After Tutorial

* Upon completing the tutorial quest, the player chooses their **starting weapon**:

  * **Sword** (melee),
  * **Wand** (magic),
  * **Bow** (ranged).
* This choice defines the player's initial combat style.
* The **Smith** building allows the player to **upgrade their current weapon** by replacing it with a higher-tier version.
* Only weapons of the chosen category become available for future upgrades.

---

## Building Upgrade System

Buildings can be upgraded to unlock new crafting tiers and more powerful items.

### Upgrade Logic

* **Smith upgrades** unlock higher tiers of weapons and tools.
* **Tailor upgrades** unlock advanced armor and larger backpacks.
* **Witch upgrades** unlock stronger potions and rare consumables.
* Buildings require gold and specific resources to upgrade.
* Higher weapon/tool tiers remain **locked** until the corresponding building is upgraded.

---

## Inventory System

The game includes a structured inventory with strict slot limits and automatic overflow management.

### Inventory Structure

* The visible inventory contains **six slots**.
* Any additional items collected beyond these six slots are moved to a **hidden inventory**, also containing **six slots**.
* If both visible and hidden inventories are full, the game displays an **"Inventory Full"** message on the UI.

### Inventory UI

* The inventory is displayed in the **top-left corner** of the screen.
* Shows currently held items and resources.
* Inventory capacity can be increased by upgrading backpacks at the Tailor (affects only slot usefulness, not the hard limit of six visible slots).

---

## UI Layout

The UI is designed to remain fixed and unaffected by player movement, using absolute positioning.

### UI Elements

1. **Top-left corner:**

   * Visible **inventory (6 slots)**.
   * **HP bar** located directly below the inventory.
   * **Total gold amount** displayed at the right end of the HP bar.

2. **Bottom center:**

   * **Currently equipped items bar**, containing:

     * Helmet slot
     * Chestplate slot
     * Leggings slot
     * Boots slot
     * **Two consumable item slots**
     * **Current weapon slot**
   * **Total character statistics** displayed directly above the equipped items bar.

All UI components stay fixed on the screen regardless of map movement to maintain constant visibility.

---

## Weapon Progression and Tutorial Restrictions

* The player starts the game with a basic **club weapon**.
* The club remains the only usable weapon until the **tutorial quest is completed**.
* After finishing the tutorial, the player chooses one of three weapon types:

  * Sword
  * Wand
  * Bow
* The chosen weapon **replaces the club**.
* All future upgrades at the Smith replace the current weapon with a stronger version from the same category.

---

## Possible Future Expansions

* Quest system
* Building upgrades
* Additional armor and weapon tiers
* Procedurally generated dungeons
* Additional biomes on the exploration map