"""
Two-Compartment Respiratory Inertance (Irs) & Dynamic Compliance Engine.
Provides deterministic, zero-dependency modeling of respiratory gas inertance, dynamic lung compliance (Cdyn),
harmonic resonant frequency (f0), and total mechanical Work of Breathing (WOB) partitioning.
"""

import math
from typing import Dict, Any, List, Optional


class RespiratoryInertanceComplianceClient:
    """
    Deterministic client for modeling respiratory system mechanical impedance components:
    inertance (gas column acceleration mass), dynamic compliance (elastance), and viscous resistance.
    Calculates mechanical Work of Breathing (WOB in Joules/L) and resonant breathing frequency.
    """

    def __init__(self):
        pass

    def evaluate_respiratory_mechanics(
        self,
        dynamic_compliance_l_cmh2o: float,
        airway_resistance_cmh2o_s_l: float,
        inertance_cmh2o_s2_l: float = 0.012,
        breathing_frequency_bpm: float = 14.0,
        tidal_volume_l: float = 0.55
    ) -> Dict[str, Any]:
        """
        Calculates resonant frequency f0 = 1 / (2 * pi * sqrt(I * C)) and Work of Breathing.
        Normative adult values:
        - Dynamic compliance: 0.050 - 0.100 L/cmH2O
        - Resistance: 1.8 - 3.8 cmH2O*s/L
        - Inertance: 0.008 - 0.020 cmH2O*s^2/L
        - WOB per breath: 0.35 - 0.70 Joules/L
        """
        if dynamic_compliance_l_cmh2o <= 0 or airway_resistance_cmh2o_s_l <= 0 or inertance_cmh2o_s2_l <= 0:
            return {"error": "Compliance, resistance, and inertance must be strictly positive"}
        if breathing_frequency_bpm <= 0 or tidal_volume_l <= 0:
            return {"error": "Frequency and tidal volume must be strictly positive"}

        # Resonant natural frequency in Hz: f0 = 1 / (2 * pi * sqrt(I * C))
        f0_hz = round(1.0 / (2.0 * math.pi * math.sqrt(inertance_cmh2o_s2_l * dynamic_compliance_l_cmh2o)), 1)

        # Work of breathing components per breath (in Joules):
        # 1 cmH2O * L = 0.0980665 Joules
        conversion_factor = 0.0980665

        # Elastic work: 0.5 * (Vt^2 / C)
        elastic_work_j = round(0.5 * (tidal_volume_l ** 2 / dynamic_compliance_l_cmh2o) * conversion_factor, 3)

        # Resistive work: (pi^2 / 4) * R * (f / 60) * Vt^2
        f_sec = breathing_frequency_bpm / 60.0
        resistive_work_j = round(((math.pi ** 2) / 4.0) * airway_resistance_cmh2o_s_l * f_sec * (tidal_volume_l ** 2) * conversion_factor, 3)

        # Inertial work: 0.5 * I * (2 * pi * f)^2 * Vt^2
        inertial_work_j = round(0.5 * inertance_cmh2o_s2_l * ((2.0 * math.pi * f_sec) ** 2) * (tidal_volume_l ** 2) * conversion_factor, 4)

        total_work_j = round(elastic_work_j + resistive_work_j + inertial_work_j, 3)
        wob_per_liter_j_l = round(total_work_j / tidal_volume_l, 2)

        # Ventilatory Work Efficiency Score (0 - 100):
        # WOB <= 0.65 J/L with normal compliance -> 90 - 100.
        # WOB > 1.40 J/L -> < 50 (High mechanical respiratory strain).
        if wob_per_liter_j_l <= 0.55:
            score = 92.0 + (0.55 - wob_per_liter_j_l) * 20.0
        elif wob_per_liter_j_l <= 0.80:
            score = 78.0 + ((0.80 - wob_per_liter_j_l) / 0.25) * 14.0
        elif wob_per_liter_j_l <= 1.20:
            score = 55.0 + ((1.20 - wob_per_liter_j_l) / 0.40) * 23.0
        else:
            score = max(5.0, 55.0 - (wob_per_liter_j_l - 1.20) * 35.0)

        mechanics_score = round(min(100.0, max(5.0, score)), 1)

        if wob_per_liter_j_l <= 0.65:
            tier = "OPTIMAL_VENTILATORY_MECHANICS"
            interp = f"Low work of breathing ({wob_per_liter_j_l} J/L, Cdyn {dynamic_compliance_l_cmh2o} L/cmH2O); high pulmonary compliance and efficient gas turnover."
            guidance = "Excellent respiratory biomechanical efficiency. Effortless ventilatory mechanics with minimal metabolic oxygen cost."
        elif wob_per_liter_j_l <= 0.95:
            tier = "NORMAL_WORK_OF_BREATHING"
            interp = f"Standard work of breathing ({wob_per_liter_j_l} J/L, resonant frequency {f0_hz} Hz); normal elastic and resistive load balance."
            guidance = "Normal ventilatory mechanics. Practice slow paced breathing (5.5 - 6 bpm) to further minimize elastic work."
        elif dynamic_compliance_l_cmh2o < 0.045:
            tier = "ELEVATED_ELASTIC_WORKLOAD"
            interp = f"Reduced dynamic compliance ({dynamic_compliance_l_cmh2o} L/cmH2O); lungs require higher pressure excursion to inflate."
            guidance = "Elevated elastic lung stiffness. Focus on thoracic spine extension, postural opening, and slow diaphragmatic inflation."
        else:
            tier = "HIGH_INERTIAL_RESISTIVE_STRAIN"
            interp = f"Elevated total work of breathing ({wob_per_liter_j_l} J/L); high resistive or frequency-dependent gas acceleration load."
            guidance = "High respiratory workload detected. Reduce hyperventilatory tachypnea, relax abdominal wall, and slow breathing cadence."

        return {
            "dynamic_compliance_l_cmh2o": dynamic_compliance_l_cmh2o,
            "airway_resistance_cmh2o_s_l": airway_resistance_cmh2o_s_l,
            "inertance_cmh2o_s2_l": inertance_cmh2o_s2_l,
            "breathing_frequency_bpm": breathing_frequency_bpm,
            "tidal_volume_l": tidal_volume_l,
            "resonant_frequency_f0_hz": f0_hz,
            "elastic_work_joules": elastic_work_j,
            "resistive_work_joules": resistive_work_j,
            "inertial_work_joules": inertial_work_j,
            "total_work_of_breathing_j_l": wob_per_liter_j_l,
            "ventilatory_mechanics_score": mechanics_score,
            "classification": tier,
            "physiological_interpretation": interp,
            "actionable_guidance": guidance
        }
