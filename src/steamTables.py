import tkinter as tk
from tkinter import ttk
from utils import get_state_properties,PROPERTY_UNITS,PROPERTY

def calculate(prop1Property,prop1Value,prop1Units,prop2Property,prop2Value,prop2Units,outputText) -> None:
    """ Runs when 'Calculate' button is pressed to calculate properties given the two states
    
        Args:
            prop1Property (str): property for Property 1
            prop1Value (str): value of Property 1 from text box
            prop1Units (str): units for Property 1
            prop2Property (str): property for Property 2
            prop2Value (str): value of Property 2 from text box
            prop2Units (str): units for Property 2
            outputText (tkinter Text): Tkinter read only text field
            
        Returns: None
    """
            

    p1Prop = prop1Property.get()
    p1Val = prop1Value.get()
    p1Unit = prop1Units.get()
    p2Prop = prop2Property.get()
    p2Val = prop2Value.get()
    p2Unit = prop2Units.get()

    outputText.config(state='normal')
    outputText.delete('1.0',tk.END)

    errormsg = validate_inputs(p1Prop,p1Val,p2Prop,p2Val)
    if errormsg:
        outputText.insert('1.0',errormsg)
    else:
        stateProperties = get_state_properties(p1Prop,p1Val,p1Unit,p2Prop,p2Val,p2Unit)
        outputText.insert(index='1.0',chars=stateProperties)

    outputText.config(state='disabled')

def update_units(propertyVar, unitCombo) -> None:
    """ Function that runs when properties are selected to update the units combo box
    
        Args:
            propteryVar (tkinter StringVar): tkinter property selection
            unitCombo (tkinter StringVar): tkinter units selection
            
        Returns: None
    
    """
    selectedProperty = propertyVar.get()
    units = PROPERTY_UNITS.get(selectedProperty, [])

    unitCombo["values"] = units
    if units:
        unitCombo.set(units[0])
    else:
        unitCombo.set("Error")

def validate_inputs(p1Prop,p1Val,p2Prop,p2Val) -> str:
    """ Validates the inputs
        Produces an error message if:
            - The two properties are identical (e.g., Pressure and Pressure)
            - A value is non numeric (e.g., entering a letter for the value)
            
        Args:
            prop1Prop (str): property for Property 1
            prop1Val (str): value of Property 1 from text box
            prop2Prop (str): property for Property 2
            prop2Val (str): value of Property 2 from text box

        Returns:
            (str) An error message (or None if there is no error)
    
    """
    errorString = None
    if p1Prop==p2Prop:
        errorString = 'Properties must cannot be the same'
    try:
        p1Val = float(p1Val)
        p2Val = float(p2Val)
    except ValueError:
        errorString = 'Values must be numeric'
    
    return errorString


def main():
    root = tk.Tk()
    root.title("Steam Table GUI")
    root.geometry("600x300")

    # -------------------------------
    # Property 1
    # -------------------------------
    tk.Label(root, text='Property 1').grid(row=0,column=0, padx=5, pady=5, sticky="w")
    prop1Property = tk.StringVar(value=PROPERTY[0])
    prop1PropertyCombo = ttk.Combobox(
        root,
        textvariable=prop1Property,
        values=PROPERTY,
        state="readonly",
        width=20
    )
    prop1PropertyCombo.grid(row=0, column=1, padx=5, pady=5)

    prop1Value = tk.StringVar()
    ttk.Entry(
        root,
        textvariable=prop1Value,
        width=15
    ).grid(row=0, column=2, padx=5, pady=5)

    prop1Units = tk.StringVar()
    prop1UnitsCombo = ttk.Combobox(
        root,
        textvariable=prop1Units,
        state="readonly",
        width=15
    )
    prop1UnitsCombo.grid(row=0, column=3, padx=5, pady=5)

    update_units(prop1Property,prop1UnitsCombo)
    prop1PropertyCombo.bind('<<ComboboxSelected>>',lambda event: update_units(prop1Property,prop1UnitsCombo))

    # -------------------------------
    # Property 2
    # -------------------------------
    tk.Label(root, text='Property 2').grid(row=1,column=0, padx=5, pady=5, sticky="w")
    prop2Property = tk.StringVar(value=PROPERTY[1])
    prop2PropertyCombo = ttk.Combobox(
        root,
        textvariable=prop2Property,
        values=PROPERTY,
        state="readonly",
        width=20
    )
    prop2PropertyCombo.grid(row=1, column=1, padx=5, pady=5)

    prop2Value = tk.StringVar()
    ttk.Entry(
        root,
        textvariable=prop2Value,
        width=15
    ).grid(row=1, column=2, padx=5, pady=5)

    prop2Units = tk.StringVar()
    prop2UnitsCombo = ttk.Combobox(
        root,
        textvariable=prop2Units,
        state="readonly",
        width=15
    )
    prop2UnitsCombo.grid(row=1, column=3, padx=5, pady=5)

    update_units(prop2Property,prop2UnitsCombo)
    prop2PropertyCombo.bind('<<ComboboxSelected>>',lambda event: update_units(prop2Property,prop2UnitsCombo))


    # -------------------------------
    # Calculate Button
    # -------------------------------
    ttk.Button(
        root,
        text="Calculate",
        command=lambda: calculate(prop1Property,prop1Value,prop1Units,prop2Property,prop2Value,prop2Units,outputText),
    ).grid(row=2, column=0, columnspan=4, pady=10)

    # -------------------------------
    # Read-Only Output Field
    # -------------------------------
    outputText = tk.Text(
        root,
        height=8,
        width=150,
        wrap="word"
    )

    outputText.grid(
        row=3,
        column=0,
        columnspan=4,
        padx=5,
        pady=10,
        sticky="nsew"
    )
    outputText.config(state='disabled')

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)

    root.mainloop()

if __name__ == "__main__":
    main()