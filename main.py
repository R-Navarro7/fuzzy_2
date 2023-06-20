from backward_chain_system import *
import argparse

def main(bonus=False):
    AEI = Backward_Chain_System()

    hipotesis = AEI.CH.keys()

    for h in hipotesis:
        AEI.check_hipotesis(h, bonus = bonus)
        if AEI.CH[h] >= AEI.alpha:
            print(f'La hipotesis "{h}" ha sido comprobada con un nivel de certeza {AEI.CH[h]}.')
        return
    # Si ninguna prediccion supera alfa se toma la con mayor valor de certeza
    vc_max = 0
    h_max = ''
    for h in hipotesis:
        if AEI.CH[h] > vc_max:
            h_max, vc_max = h, AEI.CH[h]
    if vc_max == 0:
        print(f'No se ha podido comprobar ninguna hipotesis con un nivel de certeza mayor a {AEI.alpha}')
        return
    else:
        print(f'La hipotesis "{h_max}" ha sido comprobada con un nivel de certeza {vc_max}.')
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bonus', type=str, required=True)
    args = parser.parse_args()

    if args.bonus == 'yes':
        main(bonus=True)
    elif args.bonus == 'no':
        main()
    else:
        print("Invalid argument in '--bouns' flag, please use 'yes' or 'no'.")