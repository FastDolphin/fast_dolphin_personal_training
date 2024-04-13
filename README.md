# Telegram bot for personal training

The main purpose of this tool is to provide a Telegram bot that interacts with users to manage and deliver personalized fitness-related services. 

## Main Functionality
Here’s how the bot serves its users based on the registered handlers:

- Start Interaction: Upon receiving the /start command from a user, the bot provides an initial greeting or introduction and can display basic information or navigation options.

- Menu Display: The bot offers a menu through which users can navigate various options or services offered, such as selecting different types of training plans or reports.

- Personal Training Plans: Users can engage in a conversation with the bot to set up or modify personal training plans, allowing the bot to cater to individual fitness goals.

- Callback Queries: The bot handles callback queries that arise from inline button presses in the messages, facilitating interactive and responsive user sessions that can modify settings or retrieve additional information.

- Reporting: Through conversation handlers, the bot enables users to send reports, possibly about their progress or issues, enhancing user engagement and providing tailored support.

- Authorization: The bot manages user authorization, ensuring that personalized and sensitive actions are securely handled, maintaining user trust and data integrity.

## Running the Bot

The script is designed to be executed either directly on your local machine or within a Docker container. When run, it initializes the bot and starts listening for messages from users, processing them according to the registered handlers.

### Running Locally

To run the bot locally, ensure all dependencies are installed and environment variables are set in your system or a .env file, then execute the script:

```bash
python main.py
```

### Running with Docker

For those who prefer not to tangle with local setups (or who love the pristine containment of Docker), you can run the bot inside a Docker container. Our Dockerfile ensures all the environmental needs are met without you having to manually install dependencies each time you whip up a new test environment.

### Running with Docker

For those who prefer not to tangle with local setups (or who love the pristine containment of Docker), you can run the bot inside a Docker container. Our Dockerfile ensures all the environmental needs are met without you having to manually install dependencies each time you whip up a new test environment.

#### Build the Docker image:

```bash
docker build -t telegram-bot .
```

#### Run the Docker container:

Make sure to pass the necessary environment variables that are not secret and can be hardcoded safely. For secrets, it is advised to use Docker secrets or environment variables at runtime.

```bash
docker run -e TELEGRAM_TOKEN=your_telegram_bot_token -e ADMIN_CHAT_ID=your_admin_chat_id --name my_telegram_bot telegram-bot
```

Our Dockerfile is a bit like an overprotective parent, explicitly setting environment variables like TELEGRAM_TOKEN and ADMIN_CHAT_ID. It's a helpful way to remember which keys are crucial to the bot's operation, ensuring you don't forget to pass them when spinning up the bot in a new environment. However, this verbosity in the Dockerfile also serves as a template for reminding you to inject these vital pieces of information when deploying, helping avoid those forehead-slapping moments of debugging why the bot isn't responding because someone forgot to pass the backend API URL.

## Methods and Approaches

### Factory Pattern for Handler Functions

The use of a factory pattern in creating handler functions for callback queries (callback_query_handler_factory) is crucial for a couple of reasons. First, it allows for dynamic creation of handlers with specific configurations and dependencies injected at runtime. This means the handler can be tailored to respond differently based on the configuration or the context of the request, enhancing flexibility and scalability.

Each handler created by the factory encapsulates the logic needed to process different types of callback queries, such as "get_description" and "get_personal_training". This encapsulation also helps in maintaining the separation of concerns, making the code easier to manage and debug. The factory ensures that each handler has access to necessary resources like configuration settings, logger, and messages, which are critical for the handler's operation.

### Dependency Injection (DI) Using a Container

The Container class in this implementation is an example of utilizing dependency injection to manage dependencies throughout the application. Dependency injection is a design pattern used to implement IoC (Inversion of Control), allowing for better testing and management of dependencies.

In this script:

- Configuration and Singleton Patterns: Container uses providers to manage and instantiate classes such as Config, Commands, Prompts, Updater, and Logger. Using the singleton pattern for Updater and Logger ensures that only one instance of each is created, thus conserving resources and maintaining consistency across the application.
- Separation and Management of Concerns: The container class cleanly separates the instantiation of objects from their usage, making the system easier to test and maintain. For example, the configuration for the Telegram bot token is abstracted away from the bot's operational logic.
- Flexibility and Extensibility: The use of a container allows for changes in the instantiation of dependencies with minimal impact on the system as a whole. If a different configuration or logging mechanism is needed, it can be changed in the container without affecting the rest of the application.

## ToDos:

- re-implement config with factory;

