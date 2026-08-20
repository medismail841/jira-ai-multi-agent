def get_user_request():

    print(
        "\n"
        + "=" * 60
    )

    print(
        "🤖 JIRA AI CHATBOT"
    )

    print(
        "=" * 60
    )


    print(
        "\nExemple :"
    )

    print(
        "execute KAN-1"
    )


    user_request = input(
        "\nUser : "
    ).strip()


    return user_request

if __name__ == "__main__":

    user_request = get_user_request()

    print("\nRésultat :")
    print(user_request)