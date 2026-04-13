// Basic Phaser config
const config = {
  type: Phaser.AUTO,
  width: 960,
  height: 540,
  parent: "game-container",
  backgroundColor: "#050711",
  scene: [BattleScene],
};

let game = null;

// Simple battle scene
function BattleScene() {
  Phaser.Scene.call(this, { key: "BattleScene" });
}
BattleScene.prototype = Object.create(Phaser.Scene.prototype);
BattleScene.prototype.constructor = BattleScene;

BattleScene.prototype.init = function (data) {
  this.battleData = data.battleData || null;
};

BattleScene.prototype.create = function () {
  const centerX = this.cameras.main.width / 2;
  const centerY = this.cameras.main.height / 2;

  this.add.text(centerX, 40, "YourMasterOverseer Arena", {
    fontSize: "24px",
    color: "#ffffff",
  }).setOrigin(0.5);

  // If no battle yet, show placeholder
  if (!this.battleData) {
    this.add.text(centerX, centerY, "Run a battle from the controls above", {
      fontSize: "18px",
      color: "#aaaaaa",
    }).setOrigin(0.5);
    return;
  }

  const { winner_gin, loser_gin, turns } = this.battleData;

  // For now, just use first two bots from turns
  const firstTurn = turns[0];
  const bot1Name = firstTurn.acting_name;
  const bot1Gin = firstTurn.acting_gin;
  const bot2Name = firstTurn.target_name;
  const bot2Gin = firstTurn.target_gin;

  // Card placeholders
  this.bot1Card = this.createCard(200, centerY, bot1Name, bot1Gin, 0x2b5cff);
  this.bot2Card = this.createCard(760, centerY, bot2Name, bot2Gin, 0xff2b5c);

  // Turn text
  this.turnText = this.add.text(centerX, centerY + 180, "", {
    fontSize: "16px",
    color: "#ffffff",
  }).setOrigin(0.5);

  // Animate turns
  this.currentTurnIndex = 0;
  this.turns = turns;
  this.time.addEvent({
    delay: 800,
    loop: true,
    callback: () => this.playNextTurn(),
  });
};

BattleScene.prototype.createCard = function (x, y, name, gin, color) {
  const cardWidth = 200;
  const cardHeight = 280;

  const container = this.add.container(x, y);

  const rect = this.add.rectangle(0, 0, cardWidth, cardHeight, color, 0.4)
    .setStrokeStyle(2, 0xffffff);

  const nameText = this.add.text(0, -cardHeight / 2 + 20, name, {
    fontSize: "16px",
    color: "#ffffff",
  }).setOrigin(0.5);

  const ginText = this.add.text(0, cardHeight / 2 - 20, gin, {
    fontSize: "10px",
    color: "#cccccc",
  }).setOrigin(0.5);

  container.add([rect, nameText, ginText]);
  container.baseX = x;
  container.baseY = y;
  container.cardRect = rect;
  return container;
};

BattleScene.prototype.playNextTurn = function () {
  if (!this.turns || this.currentTurnIndex >= this.turns.length) {
    this.turnText.setText("Battle complete.");
    return;
  }

  const turn = this.turns[this.currentTurnIndex];
  this.currentTurnIndex += 1;

  const isBot1Acting = turn.acting_gin === this.bot1Card.children[2].text; // ginText
  const attacker = isBot1Acting ? this.bot1Card : this.bot2Card;
  const defender = isBot1Acting ? this.bot2Card : this.bot1Card;

  const summary = `${turn.turn_number}. ${turn.acting_name} used ${turn.ability_used} — ` +
    (turn.hit ? `${turn.damage_dealt} dmg${turn.crit ? " (CRIT!)" : ""}` : "missed");

  this.turnText.setText(summary);

  // Simple attack animation
  this.tweens.add({
    targets: attacker,
    x: attacker.baseX + (isBot1Acting ? 40 : -40),
    duration: 150,
    yoyo: true,
    onComplete: () => {
      if (turn.hit) {
        // Hit shake
        this.tweens.add({
          targets: defender,
          x: defender.baseX + 10,
          duration: 60,
          yoyo: true,
          repeat: 2,
        });

        if (turn.crit) {
          defender.cardRect.setFillStyle(0xffff00, 0.6);
          this.time.delayedCall(200, () => {
            defender.cardRect.setFillStyle(defender.cardRect.fillColor, 0.4);
          });
        }
      }
    },
  });
};

// Boot game with empty scene first
window.addEventListener("load", () => {
  game = new Phaser.Game(config);

  // Wire controls
  const bot1Input = document.getElementById("bot1");
  const bot2Input = document.getElementById("bot2");
  const runBtn = document.getElementById("runBattleBtn");
  const statusEl = document.getElementById("status");

  runBtn.addEventListener("click", async () => {
    const bot1 = bot1Input.value.trim();
    const bot2 = bot2Input.value.trim();
    if (!bot1 || !bot2) {
      statusEl.textContent = "Enter both GINs.";
      return;
    }

    runBtn.disabled = true;
    statusEl.textContent = "Running battle...";

    try {
      const res = await fetch("http://127.0.0.1:8000/api/battle/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bot1_gin: bot1, bot2_gin: bot2 }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        statusEl.textContent = `Error: ${err.detail || res.status}`;
        runBtn.disabled = false;
        return;
      }
      const data = await res.json();
      statusEl.textContent = `Winner: ${data.winner_name} (${data.winner_gin})`;

      game.scene.stop("BattleScene");
      game.scene.start("BattleScene", { battleData: data });
    } catch (e) {
      console.error(e);
      statusEl.textContent = "Network error.";
    } finally {
      runBtn.disabled = false;
    }
  });
});
