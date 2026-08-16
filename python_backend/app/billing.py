class BillingModel:
    """
    Enterprise Billing Model for ACN Protocol Tasks
    """
    RATES = {
        "compute": 0.12,          # Akash / Render GPU Compute Task Rate
        "digital_worker": 0.25,   # Lead Gen / Notary / Research Worker Rate
        "automation": 0.08        # Web Scraping / Data Pipeline Task Rate
    }

    @classmethod
    def get_task_rate(cls, category: str) -> float:
        return cls.RATES.get(category.lower(), 0.10)
