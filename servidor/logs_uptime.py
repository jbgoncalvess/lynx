import time
import subprocess
from datetime import datetime


# Simplesmente esvazio o arquivo de log original e jogo sua saida em um backup, faço isso pois meu código
# de rps varre o arquivo original
def backup_e_esvaziar_log(log_file, backup_file):
    command = f"cat {log_file} >> {backup_file} && > {log_file}"
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    log_file = "/var/log/nginx/upstream_access.log"  # Arquivo de log original
    backup_file = "/var/log/nginx/backup_upstream_access.log"  # Arquivo de backup

    while True:
        backup_e_esvaziar_log(log_file, backup_file)
        print(f"[{datetime.now()}] Arquivo de log copiado para {backup_file} e esvaziado.")

        # Espera 5 minutos
        time.sleep(300)
