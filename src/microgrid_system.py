def add_source(self, source: EnergySource):
        self.sources.append(source)

    def balance_grid(self, conditions: dict, total_load_w: float):
        total_gen = sum(s.generate(conditions) for s in self.sources)
        net_power = total_gen - total_load_w
        return {"generation": total_gen, "load": total_load_w, "net": net_power}
