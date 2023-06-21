from backward_chain_system import * 
import webbrowser

def show():
    AEI = Backward_Chain_System()
    AEI_df = AEI.generar_reticulado_BR()

    with open('reticulado.html', 'w') as file:
        file.write(str(AEI_df.to_html()))
    webbrowser.open('reticulado.html')
