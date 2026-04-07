# === أضف هذه الدوال داخل class Noosphere ===

    def process_laser_impact(self, laser_beams: list[dict]):
        """
        تأثير الليزر على Noosphere (الربط الرئيسي)
        laser_beam = {"start": (x,y), "dir": (dx,dy), "frequency": float, "amplitude": float, ...}
        """
        for beam in laser_beams:
            x, y = int(beam["start"][0]), int(beam["start"][1])
            freq = beam.get("frequency", 0.5)
            amp = beam.get("amplitude", 1.0)
            
            # تأثير دائري حول نقطة الإطلاق
            radius = 4
            for i in range(-radius, radius + 1):
                for j in range(-radius, radius + 1):
                    nx, ny = x + i, y + j
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        dist = max(abs(i), abs(j))
                        resonance = amp * np.exp(-dist / radius) * 0.8
                        
                        # Resonance: التردد القريب من noosphere_field → إيجابي
                        local_field = self.noosphere_field[nx, ny]
                        freq_diff = abs(freq - local_field)
                        
                        if freq_diff < 0.25:  # رنين جيد
                            self.noosphere_field[nx, ny] += resonance * 0.6
                            self.pollution_field[nx, ny] = max(0.0, self.pollution_field[nx, ny] - resonance * 0.4)
                        else:  # رنين سيء
                            self.mental_disorder_map[nx, ny] += resonance * 0.5
                        
                        # تقليل التلوث دائمًا (تنظيف بالليزر)
                        self.pollution_field[nx, ny] *= 0.85

        self.noosphere_field = np.clip(self.noosphere_field, -1.0, 1.0)
        self.mental_disorder_map = np.clip(self.mental_disorder_map, 0.0, 1.0)

    def get_laser_modulation(self, x: int, y: int) -> dict:
        """يعطي الليزر معلومات من Noosphere (precision + stealth)"""
        coherence = self.noosphere_field[x, y]
        disorder = self.mental_disorder_map[x, y]
        
        precision_bonus = max(0.0, coherence * 0.4)          # +40% precision
        stealth_bonus = max(0.0, (1.0 - disorder) * 0.3)     # stealth أعلى عندما يكون الوعي هادئ
        
        return {
            "precision_bonus": precision_bonus,
            "stealth_bonus": stealth_bonus,
            "coherence": float(coherence)
        }
