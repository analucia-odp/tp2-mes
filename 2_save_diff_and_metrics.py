import os
import json
import subprocess
import pandas as pd
from colorama import Fore, Back, Style, init

init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.BLACK}{Back.CYAN}{Style.BRIGHT} {text} {Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'═' * 80}{Style.RESET_ALL}")

def print_subheader(text):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.WHITE}{text}{Style.RESET_ALL}")

def print_progress(message):
    print(f"{Fore.BLUE}{message}... ", end="", flush=True)

def get_instances_from_csv():
    csv_path = "instances.csv"
    if not os.path.exists(csv_path):
        print_error(f"Arquivo {csv_path} não encontrado!")
        return []
    try:
        df = pd.read_csv(csv_path)
        return df['instance_id'].unique().tolist()
    except Exception as e:
        print_error(f"Erro ao ler o CSV: {e}")
        return []

def generate_diff(repo_path=None):
    print_progress("Gerando diff das alterações")
    current_dir = os.getcwd()
    try:
        if repo_path:
            if not os.path.exists(repo_path):
                print_error(f"O caminho do repositório {repo_path} não existe!")
                return None
            os.chdir(repo_path)
            print_info(f"Trabalhando no diretório: {Fore.YELLOW}{repo_path}{Style.RESET_ALL}")

        try:
            subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                           check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print_error("Não é um repositório Git válido!")
            return None

        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )

        if not status.stdout.strip():
            print_error("Nenhuma alteração detectada no repositório!")
            return None

        diff_output = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True
        )

        if not diff_output.stdout.strip():
            subprocess.run(["git", "add", "-A"])
            diff_output = subprocess.run(
                ["git", "diff", "--staged"],
                capture_output=True,
                text=True
            )

        if not diff_output.stdout.strip():
            print_error("Não foi possível gerar o diff!")
            return None

        print_success("Diff gerado com sucesso!")
        return diff_output.stdout

    except Exception as e:
        print_error(f"Erro ao gerar diff: {e}")
        return None
    finally:
        os.chdir(current_dir)

def analyze_diff(diff_text):
    if not diff_text:
        return {}

    files_changed = 0
    files = set()
    additions = 0
    deletions = 0

    for line in diff_text.splitlines():
        if line.startswith('diff --git'):
            files_changed += 1
            parts = line.split(' b/')
            if len(parts) > 1:
                files.add(parts[1])
        elif line.startswith('+') and not line.startswith('+++'):
            additions += 1
        elif line.startswith('-') and not line.startswith('---'):
            deletions += 1

    return {
        "files_changed": files_changed,
        "files": list(files),
        "additions": additions,
        "deletions": deletions,
        "total_changes": additions + deletions
    }

def save_diff_to_json(diff_text, instance_id, model_name):
    json_path = "solutions.json"
    print_progress(f"Salvando diff no arquivo {json_path}")
    json_content = {}
    if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
        try:
            with open(json_path, 'r') as f:
                json_content = json.load(f)
        except json.JSONDecodeError:
            print_error(f"Arquivo {json_path} existe mas não é um JSON válido. Criando novo arquivo.")
            json_content = {}

    solution_key = f"{instance_id}__{model_name}"
    json_content[solution_key] = {
        "model_patch": diff_text,
        "model_name_or_path": model_name
    }

    try:
        with open(json_path, 'w') as f:
            json.dump(json_content, f, indent=2)
        print_success(f"Diff salvo com sucesso em {json_path}!")
        return True
    except Exception as e:
        print_error(f"Erro ao salvar o JSON: {e}")
        return False

def update_csv_with_metrics(instance_id, model_name, metrics):
    csv_path = "instances.csv"
    print_progress(f"Atualizando métricas no arquivo {csv_path}")
    if not os.path.exists(csv_path):
        print_error(f"Arquivo {csv_path} não encontrado!")
        return False
    try:
        df = pd.read_csv(csv_path)
        mask = (df['instance_id'] == instance_id) & (df['model'] == model_name)
        if not mask.any():
            print_error(f"Instância {instance_id} com modelo {model_name} não encontrada no CSV!")
            return False
        for key, value in metrics.items():
            if key in df.columns:
                try:
                    numeric_value = float(value)
                except ValueError:
                    numeric_value = value
                df.loc[mask, key] = numeric_value
        df.to_csv(csv_path, index=False)
        print_success(f"Métricas atualizadas com sucesso em {csv_path}!")
        return True
    except Exception as e:
        print_error(f"Erro ao atualizar o CSV: {e}")
        return False

def main():
    while True:
        repo_path_input = input(f"{Fore.CYAN}Digite o caminho do repositório (deixe em branco se já estiver no diretório correto): {Style.RESET_ALL}").strip()
        if not repo_path_input:
            repo_path = None
            break
        repo_path = os.path.abspath(repo_path_input)
        print_info(f"Você digitou o caminho: {Fore.YELLOW}{repo_path}{Style.RESET_ALL}")
        confirm = input(f"{Fore.CYAN}Esse é o caminho completo correto? (s/n): {Style.RESET_ALL}").strip().lower()
        if confirm in ('s', 'sim'):
            break
        else:
            print_warning("Por favor, digite o caminho novamente.")

    instances = get_instances_from_csv()

    if instances:
        print_subheader("Instâncias disponíveis:")
        for i, instance_id in enumerate(instances):
            print(f"{Fore.YELLOW}{i+1}{Style.RESET_ALL} - {instance_id}")

        choice = input(f"{Fore.CYAN}Selecione o número da instância (ou digite 'nova' para informar um ID manualmente): {Style.RESET_ALL}").strip()

        if choice.lower() == 'nova':
            instance_id = input(f"{Fore.CYAN}Digite o ID da instância: {Style.RESET_ALL}").strip()
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(instances):
                    instance_id = instances[idx]
                else:
                    print_error("Número inválido!")
                    instance_id = input(f"{Fore.CYAN}Digite o ID da instância: {Style.RESET_ALL}").strip()
            except ValueError:
                print_error("Entrada inválida!")
                instance_id = input(f"{Fore.CYAN}Digite o ID da instância: {Style.RESET_ALL}").strip()
    else:
        print_warning("Nenhuma instância encontrada no CSV!")
        instance_id = input(f"{Fore.CYAN}Digite o ID da instância: {Style.RESET_ALL}").strip()

    print_subheader("Qual modelo foi utilizado?")
    print(f"{Fore.YELLOW}1{Style.RESET_ALL} - Claude 3.7 Sonnet")
    print(f"{Fore.YELLOW}2{Style.RESET_ALL} - DeepSeek Chat")

    model_choice = input(f"{Fore.CYAN}Opção (1 ou 2): {Style.RESET_ALL}").strip()

    if model_choice == "1":
        model_name = "claude-3.7"
    elif model_choice == "2":
        model_name = "deepseek-chat"
    else:
        print_error("Modelo inválido! Usando 'claude-3.7' por padrão.")
        model_name = "claude-3.7"

    diff_text = generate_diff(repo_path)
    if not diff_text:
        return

    diff_metrics = analyze_diff(diff_text)
    success = save_diff_to_json(diff_text, instance_id, model_name)

    print_header("MÉTRICAS DE EXECUÇÃO")

    metrics = {}
    metrics.update(diff_metrics)

    metrics["input_tokens"] = input(f"{Fore.CYAN}Quantidade de tokens de entrada: {Style.RESET_ALL}").strip()
    metrics["output_tokens"] = input(f"{Fore.CYAN}Quantidade de tokens de saída: {Style.RESET_ALL}").strip()
    metrics["num_requests"] = input(f"{Fore.CYAN}Número de requests: {Style.RESET_ALL}").strip()
    metrics["price"] = input(f"{Fore.CYAN}Preço total (em USD): {Style.RESET_ALL}").strip()

    if success:
        update_csv_with_metrics(instance_id, model_name, metrics)

    print_header("RESUMO")
    print_info(f"Instância: {Fore.YELLOW}{instance_id}{Style.RESET_ALL}")
    print_info(f"Modelo: {Fore.YELLOW}{model_name}{Style.RESET_ALL}")
    print_info(f"Total de alterações: {Fore.YELLOW}{metrics.get('total_changes', 0)}{Style.RESET_ALL}")
    print_info(f"Arquivos alterados: {Fore.YELLOW}{metrics.get('files_changed', 0)}{Style.RESET_ALL}")
    print_info(f"Linhas adicionadas: {Fore.YELLOW}{metrics.get('additions', 0)}{Style.RESET_ALL}")
    print_info(f"Linhas removidas: {Fore.YELLOW}{metrics.get('deletions', 0)}{Style.RESET_ALL}")
    
    print_success("\nProcesso finalizado com sucesso!")

if __name__ == "__main__":
    main()
