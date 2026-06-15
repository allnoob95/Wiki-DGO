PATCH (Digimons -> Rebalance)

Substitua no seu projeto os seguintes arquivos por estes:

1) Projetos GC/Wiki-Digimon Galaxy.html
   - Aba "Digimons" agora carrega o Rebalance completo via iframe.

2) Projetos GC/Rebalance/site_rebalance_render.js
   - A tabela agora sempre mostra Status | Antes | Depois | Δ.
   - Quando não houver "antes/depois", usa "value" como fallback (Antes=Depois=value).

Depois limpe cache (Ctrl+F5) ao testar.
