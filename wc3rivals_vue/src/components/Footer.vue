<script>
    import axios from 'axios'
    export default {
        data: function() {
            return {
                db_stats: []
            }
        },
        mounted() {
            // axios
            //     .get('/v1/db/stats')
            //     .then((response) => (this.db_stats = response.data),
            //           (error) => axios.get('http://127.0.0.1:/v1/db/stats')
            //                           .then(response => (this.db_stats = response.data)));

            axios
                .get('/v1/db/stats')
                .then((response) => (this.db_stats = response.data));
        }
    }
</script>

<template>
    <footer>
        <section>
            <h3>DATABASE:</h3>
            <p v-for="ladder in db_stats" :key="ladder[0]">
                <b>{{ ladder[0] }}:</b> {{ ladder[1] }}<br>
            </p>            
        </section>
        <section></section>
        <section>
            <h3>CREDITS:</h3>
            <p>
                Alona Vinnyk,<br>
                Mykola Yakovliev
            </p>
        </section>
    </footer>
</template>

<style scoped>
footer {
    font-family: Roboto;
    font-size: 10px;
    font-weight: 400;
    font-style: normal;
    font-stretch: normal;
    line-height: 1.4;
    letter-spacing: .4px;
    color: #9c9c9c;
}
h3 {
  font-weight: bold;
}

footer section {
    margin-top: 100px;
    margin-bottom: 2em;
    float:left;
}
footer section:nth-child(1) {
    width: 30%;
}
footer section:nth-child(2) {
    width: 55%;
    min-height: 1em;
}
</style>
