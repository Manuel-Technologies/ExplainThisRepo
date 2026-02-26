import readline, { Interface as ReadlineInterface } from "node:readline";
import process from "node:process";
import { stdin as input, stderr as output } from "node:process";
import chalk from "chalk";

import { writeConfig } from "./config.js";

interface HiddenReadlineInterface extends ReadlineInterface {
  _writeToOutput: (stringToWrite: string) => void;
}

const CONFIG_TEMPLATE = `[llm]
provider = "gemini"
api_key = "{api_key}"
`;

export async function runInit(): Promise<void> {
  output.write(
    chalk.yellow(
      "WARNING: input is hidden. Paste your GEMINI_API_KEY and press Enter.\n"
    )
  );

  try {
    const apiKey = (await promptHidden("Gemini API key: ")).trim();

    if (!apiKey) {
      output.write(chalk.red("error: API key cannot be empty\n"));
      process.exit(1);
    }

    writeConfig(CONFIG_TEMPLATE.replace("{api_key}", apiKey));

    output.write(chalk.green("Configuration written.\n"));
    process.exit(0);
  } catch {
    output.write(chalk.red("\nInterrupted.\n"));
    process.exit(130);
  }
}

function promptHidden(prompt: string): Promise<string> {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input,
      output,
      terminal: true,
    }) as HiddenReadlineInterface;

    rl._writeToOutput = () => {};

    rl.question(prompt, (answer) => {
      rl.close();
      output.write("\n");
      resolve(answer);
    });
  });
}