# DeAppel

Automatiseringsscripts voor het verwerken van documenten, genereren van user stories en het deployen naar GitHub en Azure DevOps.

---

## 📋 Scripts

### `generate_userstories.py`

Verwerkt documenten (`.txt`, `.md`) in een opgegeven map en genereert hieruit user stories in Markdown-formaat.

**Gebruik:**

```bash
python3 generate_userstories.py [--input <docs_map>] [--output <uitvoerbestand>]
```

| Optie | Standaard | Omschrijving |
|-------|-----------|--------------|
| `--input` | `./docs` | Map met bronbestanden |
| `--output` | `./user_stories.md` | Uitvoerbestand (Markdown) |

**Voorbeeld:**

```bash
# Verwerk documenten in ./docs en schrijf user stories naar user_stories.md
python3 generate_userstories.py

# Gebruik een andere invoermap en uitvoerbestand
python3 generate_userstories.py --input ./requirements --output ./stories/sprint1.md
```

Het script herkent regels die voldoen aan gangbare user story-patronen (o.a. "Als gebruiker wil ik…", "As a user I want…") en schrijft ze gestructureerd weg.

---

### `deploy.sh`

Push de huidige projectwijzigingen naar GitHub (`origin`) en/of Azure DevOps (`devops`).

**Gebruik:**

```bash
./deploy.sh [--target github|devops|all] [--branch <branch>] [--message <commit-bericht>]
```

| Optie | Standaard | Omschrijving |
|-------|-----------|--------------|
| `--target` | `all` | Kies de doelomgeving: `github`, `devops` of `all` |
| `--branch` | huidige branch | Branch om te pushen |
| `--message` / `-m` | *(geen)* | Maak een commit aan met dit bericht vóór het pushen |

**Voorbeeld:**

```bash
# Verwerk documenten, commit en push naar beide remotes
python3 generate_userstories.py
./deploy.sh --message "Update user stories"

# Push alleen naar Azure DevOps
./deploy.sh --target devops

# Push een specifieke branch naar GitHub
./deploy.sh --target github --branch feature/mijn-feature
```

Zorg dat het script uitvoerbaar is:

```bash
chmod +x deploy.sh
```

---

## 🔑 SSH-configuratie

Voeg het volgende toe aan `~/.ssh/config` zodat Git automatisch de juiste sleutel kiest voor elke host:

```
# GitHub
Host github.com
    User git
    IdentityFile ~/.ssh/my_github_key

# Azure DevOps
Host ssh.dev.azure.com
    User git
    IdentityFile ~/.ssh/my_azure_key
```

Met deze configuratie werken beide remotes automatisch zonder dat je `ssh-add` handmatig hoeft uit te voeren voor elke sessie.

### Azure DevOps remote instellen

```bash
git remote add devops git@ssh.dev.azure.com:v3/<organisatie>/<project>/<repo>
```

---

## 🗂️ Projectstructuur

```
DeAppel/
├── docs/                   # Bronbestanden voor generate_userstories.py
├── generate_userstories.py # Genereert user stories uit documenten
├── deploy.sh               # Deploy-script voor GitHub en Azure DevOps
└── user_stories.md         # Gegenereerde user stories (uitvoer)
```