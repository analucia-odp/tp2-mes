#!/bin/bash

# 🧪 Envio de resultados para o benchmark SWE-bench_lite - Modo TEST
echo "🔄 Iniciando envio dos resultados no modo TEST para o SWE-bench_lite..."

sb-cli submit swe-bench_lite test --predictions_path solutions-test-claude.json --run_id solutions_split_test_claude --api_key swb_apj_UaC6OyB1BwFKwy_1ondQnCZ5lLFhPIQcFvhTij4_6833a787
status1=$?

sb-cli submit swe-bench_lite test --predictions_path solutions-test-deepseek.json --run_id solutions_split_test_deepseek --api_key swb_apj_UaC6OyB1BwFKwy_1ondQnCZ5lLFhPIQcFvhTij4_6833a787
status2=$?

if [ $status1 -eq 0 ] && [ $status2 -eq 0 ]; then
  echo "✅ Envio do modo TEST concluído com sucesso!"
else
  echo "❌ Erro ao enviar um ou ambos os resultados no modo TEST. Verifique os dados e tente novamente."
  exit 1
fi

# 🧪 Envio de resultados para o benchmark SWE-bench_lite - Modo DEV
echo "🔄 Iniciando envio dos resultados no modo DEV para o SWE-bench_lite..."

sb-cli submit swe-bench_lite dev --predictions_path solutions-dev-deepseek.json --run_id solutions_split_dev_deepseek --api_key swb_apj_UaC6OyB1BwFKwy_1ondQnCZ5lLFhPIQcFvhTij4_6833a787
status3=$?

sb-cli submit swe-bench_lite dev --predictions_path solutions-dev-claude.json --run_id solutions_split_dev_claude --api_key swb_apj_UaC6OyB1BwFKwy_1ondQnCZ5lLFhPIQcFvhTij4_6833a787
status4=$?

if [ $status3 -eq 0 ] && [ $status4 -eq 0 ]; then
  echo "✅ Envio do modo DEV concluído com sucesso!"
else
  echo "❌ Erro ao enviar um ou ambos os resultados no modo DEV. Verifique os dados e tente novamente."
  exit 1
fi

echo "🎉 Todos os envios foram realizados com sucesso!"
