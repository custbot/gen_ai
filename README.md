# DCS Agent Support

DCS Agent Support is an intelligent assistant application that leverages Azure Cognitive Search for advanced query handling, memory retention, and tool integration. The app supports both terminal-based interaction and Chainlit-powered UI for a seamless experience.

## Features
- Query contracts and invoices using Azure Cognitive Search.
- Memory retention for conversational continuity.
- Modular design with tools and dynamic workflows.
- Chainlit UI for an interactive frontend.

## Getting Started

### Prerequisites
[Conda](https://docs.conda.io/en/latest/) for managing the virtual environment.

### Setting Up the Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/custbot/gen_ai.git
   cd <repository-folder>
   ```

2. Create and activate a new virtual environment using the `environment.yml` file:
   ```bash
   conda env create -f environment.yml
   conda activate <environment-name>
   ```

### Running the App

1. Start the Chainlit app:
   ```bash
   chainlit run app.py
   ```

2. Open the browser at `http://localhost:8000` to interact with the bot.

## Usage
- Use the Chainlit UI to query contracts or invoices.
- Explore additional tools and features as defined in the application logic.

