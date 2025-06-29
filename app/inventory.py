<file name=routes.py path=/Users/mattcory/aoc_invnetory_app/app>
@main.route('/count', methods=['GET', 'POST'])
def count():
    if request.method == 'POST':
        for i in inventory_df.index:
            bin_val = request.form.get('bin_location', '').strip()
            if bin_val:
                inventory_df.at[i, 'BIN Location'] = bin_val

            case_val = request.form.get('case_count', '').strip()
            if case_val:
                inventory_df.at[i, 'Case Count'] = case_val

            bottle_val = request.form.get('bottle_count', '').strip()
            if bottle_val:
                inventory_df.at[i, 'Bottle Count'] = bottle_val
        # additional logic...
    # rest of the function...
