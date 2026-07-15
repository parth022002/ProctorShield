class ProctorAIEngine:
    @staticmethod
    def analyze_violations(log) -> tuple[float, str]:
        """
        Uses an anomaly scoring classifier to calculate the overall cheating probability (0.0 to 1.0)
        and outputs a descriptive diagnostics report explaining the reasoning.
        """
        # Individual event probabilities of cheating
        p_tab = 1.0 - (0.65 ** log.tab_switches)
        p_fs = 1.0 - (0.60 ** log.fullscreen_exits)
        p_missing = 1.0 - (0.70 ** log.face_missing)
        p_multi = 1.0 - (0.45 ** log.multiple_faces)
        p_gaze = 1.0 - (0.80 ** log.look_away)
        p_noise = 1.0 - (0.90 ** log.noise_violations)

        # Composite probability (Independent joint events formula)
        composite_prob = 1.0 - (
            (1.0 - p_tab) * 
            (1.0 - p_fs) * 
            (1.0 - p_missing) * 
            (1.0 - p_multi) * 
            (1.0 - p_gaze) * 
            (1.0 - p_noise)
        )

        # Trigger warnings and diagnostic strings
        reasons = []
        if log.tab_switches > 0:
            reasons.append(f"Tab switching detected {log.tab_switches} times (Risk: {int(p_tab*100)}%)")
        if log.fullscreen_exits > 0:
            reasons.append(f"Exited fullscreen mode {log.fullscreen_exits} times (Risk: {int(p_fs*100)}%)")
        if log.multiple_faces > 0:
            reasons.append(f"Multiple faces present in webcam {log.multiple_faces} times (Risk: {int(p_multi*100)}%)")
        if log.face_missing > 0:
            reasons.append(f"Candidate left webcam frame {log.face_missing} times (Risk: {int(p_missing*100)}%)")
        if log.look_away > 0:
            reasons.append(f"Gaze look-away alerts triggered {log.look_away} times (Risk: {int(p_gaze*100)}%)")
        if log.noise_violations > 0:
            reasons.append(f"Suspicious audio level peaks {log.noise_violations} times (Risk: {int(p_noise*100)}%)")

        # Co-occurrence analysis (threat multipliers)
        co_occurrences = []
        if log.tab_switches > 0 and log.fullscreen_exits > 0:
            composite_prob = max(composite_prob, 0.95)
            co_occurrences.append("High Threat: Concurrent tab-switching and fullscreen exits")
        if log.look_away > 0 and log.noise_violations > 0:
            composite_prob = max(composite_prob, min(1.0, composite_prob * 1.25))
            co_occurrences.append("Medium Threat: Co-occurring look-away and voice/audio signatures")

        # Final diagnostics formatting
        score_percent = int(composite_prob * 100)
        
        if score_percent < 15:
            assessment = "SECURE / CLEAN: Normal environment conditions."
        elif score_percent < 60:
            assessment = "SUSPICIOUS: Moderate distraction or alert indicators present. Review logs."
        else:
            assessment = "FLAGGED / THREAT: High likelihood of academic integrity violation."

        report = f"AI Assessment: {assessment}\n"
        if co_occurrences:
            report += f"Critical Patterns: {'; '.join(co_occurrences)}\n"
        if reasons:
            report += f"Signals: {', '.join(reasons)}."
        else:
            report += "No anomalous signals recorded."

        return float(composite_prob), report
