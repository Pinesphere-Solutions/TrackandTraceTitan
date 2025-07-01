from django.views.generic import TemplateView



class JigView(TemplateView):
    template_name = "JigLoading/Jig_Picktable.html"

class JigCompletedTable(TemplateView):
    template_name = "JigLoading/Jig_Completedtable.html"

def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

class JigCompositionView(TemplateView):
    template_name = "JigLoading/Jig_Composition.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_list = [
            {"model_no": "1805", "case_qty": 25, "case_numbers": list(range(1, 26))},
            {"model_no": "1905", "case_qty": 10, "case_numbers": list(range(1, 11))},
            {"model_no": "2222", "case_qty": 10, "case_numbers": list(range(1, 11))},
            {"model_no": "6789", "case_qty": 5, "case_numbers": list(range(1, 11))},

        ]
        # Flatten all cases with model info
        all_cases = []
        for model in model_list:
            for case in model["case_numbers"]:
                all_cases.append({
                    "model_no": model["model_no"],
                    "case_qty": model["case_qty"],
                    "case_number": case,
                })
        # Chunk into cards of 12, and collect models per card
        cards = []
        for chunk in chunk_list(all_cases, 12):
            models_in_card = []
            seen = set()
            for item in chunk:
                if item["model_no"] not in seen:
                    models_in_card.append({
                        "model_no": item["model_no"],
                        "case_qty": item["case_qty"],
                    })
                    seen.add(item["model_no"])
            cards.append({
                "models": models_in_card,
                "cases": chunk,
            })
        context["cards"] = cards
        return context