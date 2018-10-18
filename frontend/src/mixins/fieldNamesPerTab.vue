<script>
export default {

    methods: {
        getCountryField(currentSection) {
            switch (currentSection) {
                case 'export_question':
                    return 'destination_party'
                    break;
                case 'import_question':
                    return 'source_party'
                    break;
                default:
                    // statements_def
                    break;
            }
        },

        getCountryLabel(currentSection) {
            switch (currentSection) {
                case 'export_question':
                    return 'Country of Destination of Exports**'
                    break;
                case 'import_question':
                    return 'Country of Destination of Imports**'
                    break;
                default:
                    // statements_def
                    break;
            }
        }
    },


}
</script>