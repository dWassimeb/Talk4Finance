"""
Updated metadata for PowerBI dataset tables with PT replacing GL as the main fact table.
"""

# Updated dataset metadata with PT as the main fact table
DATASET_METADATA = {
    "PT": {
        "description": "Main fact table containing financial transactions and business data, replacing the former GL table",
        "type": "fact",
        "columns": {
            "EXERCICE": "Fiscal year (number)",
            "MOIS": "Month number",
            "Date Comptable": "Accounting date",
            "SOCIETE": "Company code",
            "CDR": "Cost center code",
            "CDR_LIB": "Cost center label",
            "ACTIVITE": "Activity code",
            "ACTIVITE_LIB": "Activity label",
            "PROJET": "Project code",
            "PROJET_LIB": "Project label",
            "PRODUIT": "Product code",
            "PRODUIT_LIB": "Product label",
            "Client": "Client identifier",
            "Client_Lib": "Client label",
            "COMPTE_ANALYTIQUE": "Analytical account code",
            "COMPTE_LIBELLE": "Account label",
            "MONTANT": "Amount (number)",
            "Contrepartie": "Counterpart",
            "Raison_Sociale": "Corporate name",
            "Siret_Tiers": "Third party SIRET number",
            "G_Docaposte": "Docaposte group indicator",
            "G_Softeam": "Softeam group indicator",
            "Perimetre": "Perimeter",
            "Nom_Fichier": "File name",
            "CONSO": "Consolidation indicator",
            "PROJET_CDR_KEY": "Project-CDR composite key",
            "SOCIETE_CDR_KEY": "Company-CDR composite key",
            "CPTANAL_CDR_KEY": "Analytical account-CDR composite key",
            "CPT_ANAL_KEY": "Analytical account key",
            "EXERCICE_PROJECT_KEY": "Year-Project composite key",
            "SOCIETE_ACTIVITE_KEY": "Company-Activity composite key",
            "SOCIETE_PRODUIT_KEY": "Company-Product composite key",
            "Société": "Company name",
            "Pôle": "Business pole",
            "BU": "Business unit",
            "Sous BU": "Sub business unit",
            "Marché": "Market",
            "Groupe Client": "Client group",
            "Nature de Charges": "Nature of charges",
            "Projet_RELATED": "Related project",
            "Niv1-Projet/CDR": "Level 1 project/CDR",
            "Code Produit": "Product code",
            "Activité": "Activity",
            "Client1": "Client reference",
            "NIV1_COMPTE": "Account level 1",
            "NIV2_COMPTE": "Account level 2",
            "NIV3_COMPTE": "Account level 3",
            "NIV4_COMPTE": "Account level 4",
            "NIV5_COMPTE": "Account level 5",
            "Compte Analytique": "Analytical account",
            "PRODUIT_RELATED": "Related product",
            "Société_RELATED_CDR": "Company related CDR",
            "JOURNAL": "Journal code",
            "TYPE_PIECE": "Document type",
            "SOUS_CONSO": "Sub-consolidation",
            "FLUX_SOUS_CONSO": "Sub-consolidation flow",
            "Métier": "Business line",
            "Regroupement_offre": "Offer grouping",
            "Offres": "Offers",
            "Tri_Pole": "Pole sorting (number)",
            "Regroupement PPT": "PPT grouping",
            "Tri_Regroupement_PPT": "PPT grouping sorting (number)",
            "Tri_Metier": "Business line sorting",
            "Mapping MB MN FS": "MB MN FS mapping",
            "Tri_Mapping_MB_MN_FS": "MB MN FS mapping sorting (number)",
            "SOCIETE_CDR_BU_KEY": "Company-CDR-BU composite key",
            "Client_sans_siret": "Client without SIRET",
            "NIV3_PRODUIT_RELATED": "Product level 3 related",
            "TRANSACTION": "Transaction identifier",
            "Num_Client": "Client number"
        }
    },
    "DIM_CLIENT": {
        "description": "Client dimension table containing customer information and attributes",
        "type": "dimension",
        "columns": {
            "NUM_TIERS": "Unique tier number",
            "RCU_DO": "RCU identifier for main document",
            "SIRET_DO": "SIRET number for main document",
            "RAISON_SOCIALE_DO": "Corporate name for main document",
            "RCU_FACTURE": "RCU identifier for invoice",
            "SIRET_FACTURE": "SIRET number for invoice",
            "RAISON_SOCIALE_FACTURE": "Corporate name for invoice",
            "CODE_PARTENAIRE": "Partner code",
            "FLAG_CLIENT": "Client flag (number)",
            "VILLE": "City",
            "PAYS": "Country",
            "GROUPE_COMMERCIAL": "Commercial group",
            "SS_GROUPE_COMMERCIAL_1": "Sub commercial group 1",
            "SS_GROUPE_COMMERCIAL_2": "Sub commercial group 2",
            "CATEGORIE_INSEE": "INSEE category",
            "MARCHE_HORIZONTAL": "Horizontal market",
            "MARCHE_VERTICAL": "Vertical market",
            "NOM_COMMERCIAL": "Commercial name",
            "MAIL_COMMERCIAL": "Commercial email",
            "TITRE_COMMERCIAL": "Commercial title",
            "Client": "Client identifier",
            "Client/GC": "Client/Commercial group identifier",
            "X_INSERT_DATE": "Insert date",
            "X_UPDATE_DATE": "Update date",
            "EFFECTIFS": "Workforce",
            "POLE": "Pole",
            "Client_sans_Siret": "Client without SIRET"
        }
    },
    "DIM_DATE": {
        "description": "Date dimension table for time-based analysis",
        "type": "dimension",
        "columns": {
            "DATE_FR": "French date format",
            "DATE_STANDARD": "Standard date format",
            "Année": "Year (number)",
            "Mois": "Month (number)",
            "Jour": "Day (number)",
            "DATE_VALUE": "Date value (number)",
            "Semaine": "Week (number)",
            "Trimestre": "Quarter (number)",
            "Semestre": "Semester (number)",
            "YTD": "Year to date indicator",
            "Mois-Année": "Month-Year",
            "MOIS_NOM": "Month name",
            "FIRST_DAY_OF_MONTH": "First day of month",
            "ActiveDate": "Active date",
            "Trimestre_Libelle": "Quarter label",
            "Semestre_Libelle": "Semester label",
            "Mois_Test": "Month test"
        }
    },
    "DIM_SOCIETE": {
        "description": "Company dimension table containing legal entity information",
        "type": "dimension",
        "columns": {
            "ID_SOCIETE_JURIDIQUE": "Legal entity ID (number)",
            "X_INSERT_DATE": "Insert date",
            "X_UPDATE_DATE": "Update date",
            "COMPTA": "Accounting indicator",
            "DATE_FIN_COMPTA": "Accounting end date",
            "Société": "Company name",
            "Code Société": "Company code",
            "Lib Société Juridique": "Legal entity name",
            "Lib Société Juridique Court": "Short legal entity name",
            "INTITULE_ENTITE_JURIDIQUE": "Legal entity title",
            "NUM_SOCIETE": "Company number",
            "SIRENE": "SIRENE number",
            "TVAINTRACOM": "Intra-community VAT",
            "CODE_EXCEPTION": "Exception code",
            "PAYS": "Country",
            "GROUPE": "Group",
            "BFC": "BFC indicator",
            "CONSO": "Consolidation indicator",
            "DATE_ENTREE": "Entry date",
            "DATE_SORTIE": "Exit date",
            "G_DOCAPOSTE": "Docaposte group indicator",
            "G_SOFTEAM": "Softeam group indicator",
            "G_BPO": "BPO group indicator",
            "REGROUPEMENT": "Grouping (number)"
        }
    },
    "DIM_BU": {
        "description": "Business unit dimension table",
        "type": "dimension",
        "columns": {
            "Code CDR": "CDR code",
            "CODE_SOCIETE": "Company code",
            "LIB_INTITULE_SOCIETE_JURIDIQUE": "Legal entity title label",
            "Pôle": "Business pole",
            "BU": "Business unit",
            "Sous BU": "Sub business unit",
            "NIV4_SERVICE": "Service level 4",
            "NIV5_SERVICE2": "Service level 5-2",
            "NIV5_SERVICE3": "Service level 5-3",
            "NIV6_TRADI_NUM": "Traditional number level 6",
            "Métier": "Business line",
            "TimeSheet Obligatoire": "Mandatory timesheet (number)",
            "BU_KEY": "Business unit key",
            "Offres": "Offers",
            "Sous-métier": "Sub business line",
            "Type Croissance": "Growth type",
            "Regroupement_Offre": "Offer grouping",
            "Tri_Pole": "Pole sorting (number)"
        }
    },
    "TRI_POLE": {
        "description": "Pole sorting reference table",
        "type": "dimension",
        "columns": {
            "Pôle": "Business pole",
            "Tri_Pôle": "Pole sorting order"
        }
    },
    "TRI_METIER": {
        "description": "Business line sorting reference table",
        "type": "dimension",
        "columns": {
            "METIER": "Business line",
            "TRI_METIER": "Business line sorting order"
        }
    },
    "DIM_MARGE": {
        "description": "Margin dimension table",
        "type": "dimension",
        "columns": {
            "NIV_MARGE_N_1": "Margin level N-1",
            "PPT": "PPT indicator",
            "SOCIETE_CDR_KEY": "Company-CDR composite key",
            "Tri_Mapping": "Mapping sorting (number)",
            "NIV_MARGE_N": "Margin level N"
        }
    },
    "TRI_MAPPING_MB_MN_FS": {
        "description": "MB MN FS mapping sorting reference table",
        "type": "dimension",
        "columns": {
            "MAPPING MB MN FS": "MB MN FS mapping",
            "TRI MAPPING": "Mapping sorting (number)"
        }
    },
    "MAPPING_ACTIVITE": {
        "description": "Activity mapping table by company and fiscal year",
        "type": "dimension",
        "columns": {
            "EXERCICE": "Fiscal year",
            "Activité": "Activity code",
            "Description": "Activity description",
            "Niv1_Activité": "Activity hierarchy level 1",
            "Niv2_Activité": "Activity hierarchy level 2",
            "Niv3_Activité": "Activity hierarchy level 3",
            "Niv4_Activité": "Activity hierarchy level 4",
            "Niv5_Activité": "Activity hierarchy level 5",
            "Code Société": "Company code",
            "SOCIETE_ACTIVITE_KEY": "Company-Activity composite key"
        }
    },
    "MAPPING_PRODUIT": {
        "description": "Product mapping table by company and fiscal year",
        "type": "dimension",
        "columns": {
            "EXERCICE": "Fiscal year",
            "Code Produit": "Product code",
            "Produit": "Product name",
            "Niv1_CRM": "Product hierarchy level 1 in CRM",
            "Niv2_CRM": "Product hierarchy level 2 in CRM",
            "Niv3_CRM": "Product hierarchy level 3 in CRM",
            "Niv4_CRM": "Product hierarchy level 4 in CRM",
            "Niv5_CRM": "Product hierarchy level 5 in CRM",
            "BU PROD": "Business unit producing the product",
            "REF_CAT_CRM": "CRM category reference",
            "CODE SOCIETE": "Company code",
            "LIB_SOC_REG": "Regional company name",
            "SOCIETE_PRODUIT_KEY": "Company-Product composite key",
            "CODE_NOM_PRODUIT": "Product code and name composite"
        }
    },
    "MAPPING_PROJET_MULTIBU": {
        "description": "Multi-business unit project mapping table",
        "type": "dimension",
        "columns": {
            "EXERCICE": "Fiscal year",
            "Code Projet": "Project code",
            "NIV1_PROJET": "Project hierarchy level 1",
            "NIV2_PROJET": "Project hierarchy level 2",
            "NIV3_PROJET": "Project hierarchy level 3",
            "NIV4_PROJET": "Project hierarchy level 4",
            "NIV5_PROJET": "Project hierarchy level 5",
            "Mapping Immobilier": "Real estate mapping",
            "Num Opportunité CRM": "CRM opportunity number",
            "EXERCICE_PROJECT_KEY": "Year-Project composite key",
            "LIB_PROJET": "Project label"
        }
    },
    "MAPPING_PROJET_CDR": {
        "description": "Project-CDR mapping table",
        "type": "dimension",
        "columns": {
            "EXERCICE": "Fiscal year",
            "Code Projet": "Project code",
            "Niv1-Projet/CDR": "Project/CDR hierarchy level 1",
            "Niv2-Projet/CDR": "Project/CDR hierarchy level 2",
            "Niv3-Projet/CDR": "Project/CDR hierarchy level 3",
            "Niv4-Projet/CDR": "Project/CDR hierarchy level 4",
            "Niv5-Projet/CDR": "Project/CDR hierarchy level 5",
            "Mapping Immobilier": "Real estate mapping",
            "Num Opportunité CRM": "CRM opportunity number",
            "CDR Associé": "Associated CDR",
            "PROJET_CDR_KEY": "Project-CDR composite key",
            "PROJET": "Project identifier",
            "LIB_PROJET": "Project label"
        }
    },
    "MAPPING_COMPTE": {
        "description": "Account mapping table for analytical and magnitude accounts",
        "type": "dimension",
        "columns": {
            "Compte Analytique": "Analytical account code",
            "Lib Compte Analytique": "Analytical account label",
            "Mapping Niveau 1": "Account mapping level 1",
            "Mapping Niveau 2": "Account mapping level 2",
            "NIV3_COMPTE": "Account mapping level 3",
            "NIV4_COMPTE": "Account mapping level 4",
            "NIV5_COMPTE": "Account mapping level 5",
            "Compte Magnitude": "Magnitude account code",
            "Lib Compte Magnitude": "Magnitude account label",
            "NIV1_MAGNITUDE": "Magnitude mapping level 1",
            "NIV2_MAGNITUDE": "Magnitude mapping level 2",
            "NIV3_MAGNITUDE": "Magnitude mapping level 3",
            "NIV4_MAGNITUDE": "Magnitude mapping level 4",
            "CPT_ANAL_KEY": "Analytical account primary key",
            "REGROUPEMENT_PPT": "PPT grouping for financial presentation",
            "TYPE_COMPTE": "Account type",
            "Tri_Regroupement_PPT": "PPT grouping sorting order"
        }
    },
    "TRI_REGROUPEMENT_PPT": {
        "description": "PPT grouping sorting reference table",
        "type": "dimension",
        "columns": {
            "Regroupement_PPT": "PPT grouping",
            "Tri": "Sorting order"
        }
    },
    "INDICATEURS": {
        "description": "Table containing business indicators and financial measures - contains calculated measures and expressions rather than traditional columns",
        "type": "measures",
        "columns": {}
    }
}

# Updated relationships reflecting the new PT-centered star schema
RELATIONSHIPS = [
    {"from_table": "PT", "from_key": "Num_Client", "to_table": "DIM_CLIENT", "to_key": "NUM_TIERS",
     "description": "Links transactions to clients"},

    {"from_table": "PT", "from_key": "SOCIETE_ACTIVITE_KEY", "to_table": "MAPPING_ACTIVITE", "to_key": "SOCIETE_ACTIVITE_KEY",
     "description": "Links transactions to activities by company"},

    {"from_table": "PT", "from_key": "SOCIETE_PRODUIT_KEY", "to_table": "MAPPING_PRODUIT", "to_key": "SOCIETE_PRODUIT_KEY",
     "description": "Links transactions to products by company"},

    {"from_table": "PT", "from_key": "Date Comptable", "to_table": "DIM_DATE", "to_key": "DATE_STANDARD",
     "description": "Links transactions to dates"},

    {"from_table": "PT", "from_key": "SOCIETE", "to_table": "DIM_SOCIETE", "to_key": "Code Société",
     "description": "Links transactions to companies"},

    {"from_table": "PT", "from_key": "SOCIETE_CDR_BU_KEY", "to_table": "DIM_BU", "to_key": "BU_KEY",
     "description": "Links transactions to business units"},

    {"from_table": "DIM_BU", "from_key": "Pôle", "to_table": "TRI_POLE", "to_key": "Pôle",
     "description": "Links business units to pole sorting"},

    {"from_table": "DIM_BU", "from_key": "Métier", "to_table": "TRI_METIER", "to_key": "METIER",
     "description": "Links business units to business line sorting"},

    {"from_table": "PT", "from_key": "SOCIETE_CDR_KEY", "to_table": "DIM_MARGE", "to_key": "SOCIETE_CDR_KEY",
     "description": "Links transactions to margin analysis"},

    {"from_table": "DIM_MARGE", "from_key": "NIV_MARGE_N", "to_table": "TRI_MAPPING_MB_MN_FS", "to_key": "MAPPING MB MN FS",
     "description": "Links margin data to MB MN FS mapping"},

    {"from_table": "PT", "from_key": "EXERCICE_PROJECT_KEY", "to_table": "MAPPING_PROJET_MULTIBU", "to_key": "EXERCICE_PROJECT_KEY",
     "description": "Links transactions to multi-BU projects"},

    {"from_table": "PT", "from_key": "PROJET_CDR_KEY", "to_table": "MAPPING_PROJET_CDR", "to_key": "PROJET_CDR_KEY",
     "description": "Links transactions to project-CDR mappings"},

    {"from_table": "PT", "from_key": "CPT_ANAL_KEY", "to_table": "MAPPING_COMPTE", "to_key": "CPT_ANAL_KEY",
     "description": "Links transactions to analytical accounts"},

    {"from_table": "MAPPING_COMPTE", "from_key": "REGROUPEMENT_PPT", "to_table": "TRI_REGROUPEMENT_PPT", "to_key": "Regroupement_PPT",
     "description": "Links account mappings to PPT grouping sorting"}
]