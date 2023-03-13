# MEDICS2.0-sous-chef
Définition du sous-chef, représentant l'exécutant de chacune des étapes individuelles du traitement spécifique à MEDICS 2.0.  

Un sous-chef écoute sur un canal sur lequel il se fait notifier lorsque qu'il doit démarrer son traitement type de traitement. Il est déployé avec un configuration spécifique qui lui permet de savoir comment démarrer le traitement, selon les étapes suivantes:

1. Setup de l'environnement sur la plateforme de calcul
1.1 Pull image du container encapsulant le code à exécuter
1.2 Mount l'image médicale à traiter à partir du storage S3

2. Exécution du traitement sur la plateforme de calcul
2.1 Exécuter le script SLURM pour spécifier les ressources allouées et pour build le container singularity
2.2 Exécuter la commande SLURM pour envoyer la job à la plateforme de calcul
