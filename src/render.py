from tabulate import tabulate


def render_result(results):
    headers = ["Item", "Descrição", "Status", "Comentários"]
    data = []

    for result in results:
        data.append([result["item"],
                     result["description"],
                     result["status"],
                     result["comments"]])

    print(tabulate(data, headers=headers, maxcolwidths=[10, 80, 10, 50], tablefmt="simple_grid"))
