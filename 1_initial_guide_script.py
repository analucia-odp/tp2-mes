import os
import random
import pandas as pd
from datasets import load_dataset
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

def print_code(text):
    print(f"{Fore.GREEN}{Back.BLACK} {text} {Style.RESET_ALL}")

def print_progress(message):
    print(f"{Fore.BLUE}{message}... ", end="", flush=True)

def extract_github_url(repo_name):
    return f"https://github.com/{repo_name}"

def setup_csv_file():
    csv_path = "instances.csv"
    columns = ['instance_id', 'repo', 'base_commit', 'split', 
               'model', 'input_tokens', 'output_tokens', 'num_requests', 'price',
               'total_changes', 'files_changed', 'additions', 'deletions']
    if not os.path.exists(csv_path):
        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_path, index=False)
        print_success(f"Arquivo criado em {csv_path}")
    else:
        df = pd.read_csv(csv_path)
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df.to_csv(csv_path, index=False)
    return csv_path

def get_used_instances(csv_path):
    df = pd.read_csv(csv_path)
    return df['instance_id'].unique().tolist()

def record_instances(csv_path, instance_id, repo, base_commit, split):
    df = pd.read_csv(csv_path)
    models = ['claude-3.7', 'deepseek-chat']
    new_rows = []
    for model in models:
        if not ((df['instance_id'] == instance_id) & (df['model'] == model)).any():
            new_rows.append({
                'instance_id': instance_id,
                'repo': repo,
                'base_commit': base_commit,
                'split': split,
                'model': model,
                'input_tokens': "",
                'output_tokens': "",
                'num_requests': "",
                'price': "",
                'total_changes': "",
                'files_changed': "",
                'additions': "",
                'deletions': ""
            })
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_csv(csv_path, index=False)
        print_success(f"Instâncias para {instance_id} criadas no arquivo de rastreamento para os dois modelos.")

def find_instance(dataset, instance_id):
    for split in ['dev', 'test']:
        split_data = dataset[split]
        for idx, instance in enumerate(split_data):
            if instance['instance_id'] == instance_id:
                return instance, split
    return None, None

def create_prompt(instance):
    problem_statement = instance['problem_statement']
    prompt_content = (
        f"Você é um assistente de desenvolvimento especializado em resolver problemas de código.\n\n"
        f"A seguir está um problema real de um repositório que precisa ser corrigido.\n\n"
        f"Repositório: {instance['repo']}\n"
        f"Descrição do problema:\n{problem_statement}\n\n"
        f"Por favor, realize apenas as modificações necessárias no código-fonte para resolver esse problema.\n"
        f"Para referência, o seguinte patch de teste será utilizado para validar sua solução:\n\n{instance['test_patch']}\n\n"
        f"Analise cuidadosamente o patch de teste para entender o comportamento esperado.\n"
        f"Importante: concentre-se exclusivamente nas alterações necessárias para corrigir o problema específico.\n"
        f"Não modifique nenhum teste. O patch de teste fornecido serve somente para referência; "
        f"não execute comandos no terminal nem rode testes para validar a implementação."
    )
    return prompt_content

def main():
    csv_path = setup_csv_file()
    used_instances = get_used_instances(csv_path)
    
    print_progress("Carregando o dataset SWE-bench Lite")
    swe_bench_dataset = load_dataset('princeton-nlp/SWE-bench_Lite')
    print_success("Dataset carregado com sucesso!")
    
    print_header("SELEÇÃO DE INSTÂNCIA")
    print_info("Selecione uma opção:")
    print(f"{Fore.YELLOW}1{Style.RESET_ALL} - Escolher uma instância aleatória")
    print(f"{Fore.YELLOW}2{Style.RESET_ALL} - Fornecer um ID de instância específico")
    
    choice = ""
    while choice not in ["1", "2"]:
        choice = input(f"{Fore.CYAN}Opção (1 ou 2): {Style.RESET_ALL}").strip()
    
    if choice == "2":
        instance_id = input(f"{Fore.CYAN}Digite o ID da instância desejada: {Style.RESET_ALL}").strip()
        if instance_id in used_instances:
            print_error(f"A instância {instance_id} já foi utilizada. Por favor, escolha outra.")
            return
        print_progress(f"Procurando instância {instance_id}")
        instance, split = find_instance(swe_bench_dataset, instance_id)
        if not instance:
            print_error(f"Instância {instance_id} não encontrada no dataset.")
            return
    else:
        print_progress("Selecionando uma instância aleatória")
        available_instances = []
        for split in ['dev', 'test']:
            split_data = swe_bench_dataset[split]
            for idx, instance in enumerate(split_data):
                current_id = instance['instance_id']
                if current_id not in used_instances:
                    available_instances.append((current_id, instance, split))
        if not available_instances:
            print_error("Todas as instâncias já foram utilizadas!")
            return
        instance_id, instance, split = random.choice(available_instances)
        print_success(f"Instância selecionada aleatoriamente: {instance_id}")
    
    record_instances(csv_path, instance_id, instance['repo'], instance['base_commit'], split)
    
    print_header("DETALHES DA INSTÂNCIA")
    print_info(f"ID: {Fore.YELLOW}{instance_id}{Style.RESET_ALL} (do split {Fore.YELLOW}{split}{Style.RESET_ALL})")
    print_info(f"Repositório: {Fore.YELLOW}{instance['repo']}{Style.RESET_ALL}")
    print_info(f"Commit Base: {Fore.YELLOW}{instance['base_commit']}{Style.RESET_ALL}")
    
    print_header("INSTRUÇÕES DE CONFIGURAÇÃO")
    github_url = extract_github_url(instance['repo'])
    
    print_subheader("1. Clone o repositório:")
    print_code(f"git clone {github_url}")
    
    print_subheader("2. Navegue até o diretório do repositório:")
    print_code(f"cd {instance['repo'].split('/')[-1]}")
    
    print_subheader("3. Faça checkout do commit base:")
    print_code(f"git checkout {instance['base_commit']}")
    
    print_header("CONTEXTO PARA A IA")
    print_warning("Ao fornecer contexto para a IA, inclua APENAS:")
    print_info("✓ Os arquivos fonte (geralmente em pastas 'src' ou similares)")
    print_info("✓ Arquivos de teste (geralmente em pastas 'test' ou similares)")
    print_error("✗ NÃO inclua arquivos grandes de dependências, artefatos de build ou código gerado")
    
    print_header("PROMPT SUGERIDO PARA A IA")
    prompt = create_prompt(instance)
    print(f"{Fore.WHITE}{prompt}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
