<template>
    <div id="wizardPage">
            <v-stepper v-model="stepNumber" vertical>
                <v-stepper-step step="1" v-bind:complete="stepNumber > 1">Создание вопроса</v-stepper-step>
                <v-stepper-content step="1">
                    <v-layout row>
                        <v-flex>
                            <v-text-field
                                    v-model="question"
                                    name="input-question"
                                    label="Ввод вопроса">
                            </v-text-field>
                        </v-flex>
                    </v-layout>
                    <v-btn class="primary" @click.native="stepNumber = 2">Продолжить</v-btn>
                </v-stepper-content>

                <v-stepper-step step="2" v-bind:complete="stepNumber > 2">Добавление эталонных ответов</v-stepper-step>
                <v-stepper-content step="2">
                    <v-layout row>
                        Вопрос: {{ question }}
                    </v-layout>
                    <v-layout row v-for="(answer, index) in answers" >
                        <v-flex xs10>
                            <v-text-field
                                    v-model="answers[index]"
                                    label="Ввод ответа"
                            ></v-text-field>
                        </v-flex>
                        <v-btn fab v-if="answers.length != 1" @click.native="answers.splice(index,1)" small dark class="red">
                            <v-icon dark>remove</v-icon>
                        </v-btn>
                        <v-btn v-if="index == (answers.length-1)" @click.native="answers.push('')" fab small dark class="green">
                            <v-icon dark>add</v-icon>
                        </v-btn>
                    </v-layout>
                    <v-btn class="primary" @click="buildRelations">Продолжить</v-btn>
                    <v-btn @click.native="stepNumber = 1">Назад</v-btn>
                </v-stepper-content>

                <v-stepper-step step="3" v-bind:complete="stepNumber > 3">Редактирование критериев</v-stepper-step>
                <v-stepper-content step="3">
                    <div class="text-xs-center">
                        <v-progress-circular indeterminate v-if="loading" v-bind:size="80" v-bind:width="5" style="color: royalblue"></v-progress-circular>
                    </div>
                    <v-data-table
                            v-if="!loading"
                            v-bind:headers="relationsTableHeader"
                            v-bind:items="relations"
                            v-model="selectedRelations"
                            select-all
                            hide-actions
                            selected-key="id"
                            no-data-text="Проведите анализ или добавьте связи вручную"
                            class="elevation-1"
                    >
                        <template slot="items" scope="props">
                            <td class="text-xs-right">
                                <v-checkbox
                                        primary
                                        v-model="props.selected"
                                ></v-checkbox>
                            </td>
                            <td>{{ props.item.words.map(w => w['value']).join(' ') }}</td>
                            <td class="text-xs-right">
                                <v-edit-dialog lazy>
                                    {{ props.item.weight }}
                                    <v-text-field
                                            type="number"
                                            slot="input"
                                            label="Edit"
                                            v-model="props.item.weight"
                                            single-line counter="counter"
                                    ></v-text-field>
                                </v-edit-dialog>
                            </td>
                            <td class="text-xs-right">{{ props.item.relation }}</td>
                            <td class="text-xs-right">
                                <v-edit-dialog lazy>
                                    {{ props.item.group }}
                                    <v-text-field
                                            type="number"
                                            slot="input"
                                            label="Edit"
                                            v-model="props.item.group"
                                            single-line counter="counter"
                                    ></v-text-field>
                                </v-edit-dialog>
                            </td>
                        </template>

                        <!--<template slot="footer">-->
                            <!--<tr>-->
                                <!--<td style="width:20px"></td>-->
                                <!--<td style="padding-left: 20px">-->
                                    <!--<v-text-field @keyup.enter="addLink" v-model="newWord" label="Слово"></v-text-field>-->
                                <!--</td>-->
                                <!--<td style="padding-left: 10% ;width: 10px">-->
                                    <!--<v-text-field @keyup.enter="addLink" v-model="newWeight" label="Вес"></v-text-field>-->
                                <!--</td>-->
                                <!--<td style="padding-left: 3% ;width: 10px">custom</td>-->
                                <!--<td style="padding-left: 4% ;width: 10px">false</td>-->
                            <!--</tr>-->
                        <!--</template>-->
                    </v-data-table>
                    <v-layout row>
                        <v-btn class="primary" @click.native="stepNumber = 4">Продолжить</v-btn>
                        <v-btn @click.native="stepNumber = 2">Назад</v-btn>
                    </v-layout>
                </v-stepper-content>

                <v-stepper-step step="4">Подтверждение результата</v-stepper-step>
                <v-stepper-content step="4">
                    <v-layout row>Вопрос: {{question}}</v-layout>
                    <v-layout row v-for="(answer, index) in answers">Ответ {{index}}: {{answer}}</v-layout>
                    <v-layout row v-for="(link, index) in selectedRelations">Связь {{index}}: {{link}}</v-layout>
                    <v-btn @click="save" class="primary">Сохранить</v-btn>
                    <v-btn @click.native="stepNumber = 3">Назад</v-btn>
                </v-stepper-content>
            </v-stepper>
    </div>
</template>
<script>
    export default{
        data () {
            return {
                stepNumber: 1,
                relationsTableHeader: [
                    {text: 'Слова', value: 'words', align: 'left'},
                    {text: 'Вес', value: 'weight'},
                    {text: 'Связь (UD)', value: 'relation'},
                    {text: 'Группа', value: 'group'}
                ],

                question: '',
                answers: [''],

                relations: [],
                selectedRelations: [],

                loading: false
            }
        },
        methods: {
            buildRelations(){
                let self = this
                self.stepNumber = 3
                self.relations = []
                self.selectedRelations = []
                self.loading = true
                this.$http.post('http://localhost:8000/build_relations', {answers: this.answers}).then(response => {
                    self.relations = response.body
                    self.loading = false
                })
            },
            save(){
                let self = this
                self.$http.post('http://localhost:8000/wizard_save', {
                    question: self.question, answers: self.answers, relations: self.selectedRelations}
                ).then(response => { //success
                    if(response.ok){
                        self.stepNumber = 1
                        self.relations = []
                        self.selectedRelations = []
                        self.question = ''
                        self.answers = ['']
                    }
                }, response => { //error
                    //todo: error alert
                })
            }
        }
    }
</script>