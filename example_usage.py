"""
Example Usage: Respiratory Inertance (Irs) & Dynamic Compliance Evaluation.
Demonstrates calculation of mechanical Work of Breathing (WOB) and resonant frequency (f0).
"""

from client import RespiratoryInertanceComplianceClient


def main():
    client = RespiratoryInertanceComplianceClient()
    print("=== Respiratory Inertance & Dynamic Compliance Demo ===")

    # Test Case 1: Healthy normal resting ventilation
    res1 = client.evaluate_respiratory_mechanics(
        dynamic_compliance_l_cmh2o=0.075,
        airway_resistance_cmh2o_s_l=2.40,
        inertance_cmh2o_s2_l=0.012,
        breathing_frequency_bpm=14.0,
        tidal_volume_l=0.55
    )
    print("\nTest Case 1: Healthy Normal Mechanics")
    print(f"  Compliance (Cdyn): {res1['dynamic_compliance_l_cmh2o']} L/cmH2O | Resistance: {res1['airway_resistance_cmh2o_s_l']} cmH2O*s/L")
    print(f"  Resonant Frequency (f0): {res1['resonant_frequency_f0_hz']} Hz")
    print(f"  Work Breakdown: Elastic {res1['elastic_work_joules']} J | Resistive {res1['resistive_work_joules']} J | Inertial {res1['inertial_work_joules']} J")
    print(f"  Total WOB: {res1['total_work_of_breathing_j_l']} Joules/L")
    print(f"  Mechanics Score: {res1['ventilatory_mechanics_score']} / 100")
    print(f"  Classification: {res1['classification']}")
    print(f"  Guidance: {res1['actionable_guidance']}")

    # Test Case 2: Stiff lungs / reduced compliance (Elevated elastic work)
    res2 = client.evaluate_respiratory_mechanics(
        dynamic_compliance_l_cmh2o=0.032,
        airway_resistance_cmh2o_s_l=3.20,
        breathing_frequency_bpm=20.0,
        tidal_volume_l=0.50
    )
    print("\nTest Case 2: Reduced Compliance / High Elastic Load")
    print(f"  Compliance: {res2['dynamic_compliance_l_cmh2o']} L/cmH2O | Total WOB: {res2['total_work_of_breathing_j_l']} J/L")
    print(f"  Mechanics Score: {res2['ventilatory_mechanics_score']} / 100")
    print(f"  Classification: {res2['classification']}")
    print(f"  Guidance: {res2['actionable_guidance']}")


if __name__ == "__main__":
    main()
