import streamlit as st
import streamlit.components.v1 as components


def inject_pwa_tags():
    """Suntik tag PWA manifest & service worker ke dalam <head> utama Streamlit."""
    components.html(
        """
        <script>
            const parentDoc = window.parent.document;

            if (!parentDoc.querySelector('link[rel="manifest"]')) {
                const manifest = parentDoc.createElement('link');
                manifest.rel = 'manifest';
                manifest.href = '/app/static/manifest.json';
                parentDoc.head.appendChild(manifest);
            }

            if (!parentDoc.querySelector('meta[name="apple-mobile-web-app-capable"]')) {
                const appleMeta = parentDoc.createElement('meta');
                appleMeta.name = 'apple-mobile-web-app-capable';
                appleMeta.content = 'yes';
                parentDoc.head.appendChild(appleMeta);
            }

            if ('serviceWorker' in window.parent.navigator) {
                window.parent.navigator.serviceWorker
                    .register('/app/static/sw.js')
                    .catch(err => console.log('Service Worker gagal didaftar:', err));
            }
        </script>
        """,
        height=0,
    )


def main():
    st.set_page_config(
        page_title="Kalkulator Zakat Pendapatan Selangor 2026",
        page_icon="🕌",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    inject_pwa_tags()

    st.title("🕌 Kalkulator Zakat Pendapatan")
    st.caption("Berdasarkan ketetapan Lembaga Zakat Selangor (LZS) bagi tahun 2026")
    st.divider()

    # PILIHAN PENGGAL NISAB & KAEDAH PENGIRAAN
    st.subheader("Tetapan Taksiran")
    col_set1, col_set2 = st.columns(2)
    with col_set1:
        nisab_options = {
            "Julai – Disember 2026 (RM 38,748)": 38748.00,
            "Januari – Jun 2026 (RM 42,047)": 42047.00,
        }
        nisab_label = st.selectbox("Tempoh Nisab Semasa", list(nisab_options.keys()))
        nisab = nisab_options[nisab_label]

    with col_set2:
        kaedah = st.selectbox(
            "Kaedah Pengiraan",
            [
                "Dengan Tolakan (Had Kifayah & KWSP)",
                "Tanpa Tolakan (Pendapatan Kasar)",
            ],
        )

    # SEKSYEN 1: PENDAPATAN SETAHUN
    st.header("1. Pendapatan Setahun (A)")
    col1, col2 = st.columns(2)
    with col1:
        gaji_bulan = st.number_input("Gaji Kasar Sebulan (RM)", min_value=0.0, step=100.0)
    with col2:
        bonus = st.number_input("Bonus / Elaun Tahunan (RM)", min_value=0.0, step=100.0)

    pendapatan_lain = st.number_input(
        "Pendapatan Lain Setahun — Sewa, Freelance, Hibah dll. (RM)",
        min_value=0.0,
        step=100.0,
    )

    jumlah_pendapatan = (gaji_bulan * 12) + bonus + pendapatan_lain

    # SEKSYEN 2: TOLAKAN (JIKA KAEDAH DENGAN TOLAKAN DIPILIH)
    kwsp = 0.0
    had_kifayah = 0.0

    if kaedah == "Dengan Tolakan (Had Kifayah & KWSP)":
        st.header("2. Tolakan KWSP & Had Kifayah")

        auto_kwsp = st.toggle("Tolak Caruman KWSP Pekerja (11%)", value=True)
        if auto_kwsp:
            kwsp = (gaji_bulan * 12 + bonus) * 0.11
            st.caption(f"Anggaran caruman KWSP 11%: **RM {kwsp:,.2f}** setahun")
        else:
            kwsp = st.number_input(
                "Jumlah Caruman KWSP Setahun (RM)", min_value=0.0, step=100.0
            )

        ketua_keluarga = st.toggle(
            "Saya ialah Ketua Keluarga (Tolakan Asas RM 14,580)", value=True
        )

        with st.expander("Senarai Tanggungan Isi Rumah (Klik untuk isi)", expanded=False):
            col3, col4 = st.columns(2)
            with col3:
                dewasa_bekerja = st.number_input(
                    "Dewasa Bekerja (18+ thn)", min_value=0, step=1, help="RM 4,944 / seorang"
                )
                dewasa_x_bekerja = st.number_input(
                    "Dewasa Tidak Bekerja / Pasangan", min_value=0, step=1, help="RM 2,004 / seorang"
                )
                anak_ipt = st.number_input(
                    "Tanggungan Belajar di IPT", min_value=0, step=1, help="RM 7,356 / seorang"
                )
                anak_7_17 = st.number_input(
                    "Anak Berumur 7 – 17 Tahun", min_value=0, step=1, help="RM 4,896 / seorang"
                )
            with col4:
                anak_bawah_6 = st.number_input(
                    "Anak 6 Tahun & Ke Bawah", min_value=0, step=1, help="RM 2,100 / seorang"
                )
                oku = st.number_input(
                    "Tambahan: Tanggungan OKU", min_value=0, step=1, help="RM 2,964 / seorang"
                )
                sakit = st.number_input(
                    "Tambahan: Pesakit Kronik", min_value=0, step=1, help="RM 2,916 / seorang"
                )
                taska = st.number_input(
                    "Tambahan: Kos Taska / Asuhan", min_value=0, step=1, help="RM 3,960 / seorang"
                )

        if ketua_keluarga:
            had_kifayah += 14580.0

        had_kifayah += (
            (dewasa_bekerja * 4944.0)
            + (dewasa_x_bekerja * 2004.0)
            + (anak_ipt * 7356.0)
            + (anak_7_17 * 4896.0)
            + (anak_bawah_6 * 2100.0)
            + (oku * 2964.0)
            + (sakit * 2916.0)
            + (taska * 3960.0)
        )

    # PENGIRAAN AKHIR
    jumlah_tolakan = kwsp + had_kifayah
    pendapatan_berzakat = max(0.0, jumlah_pendapatan - jumlah_tolakan)
    wajib_zakat = pendapatan_berzakat >= nisab and jumlah_pendapatan > 0
    jumlah_zakat_tahun = pendapatan_berzakat * 0.025 if wajib_zakat else 0.0
    jumlah_zakat_bulan = jumlah_zakat_tahun / 12

    # SEKSYEN 3: RINGKASAN & KEPUTUSAN
    st.divider()
    st.header("3. Ringkasan & Keputusan")

    m1, m2, m3 = st.columns(3)
    m1.metric("Pendapatan Kasar", f"RM {jumlah_pendapatan:,.2f}")
    m2.metric("Jumlah Tolakan", f"RM {jumlah_tolakan:,.2f}")
    m3.metric("Baki Layak Zakat", f"RM {pendapatan_berzakat:,.2f}")

    if jumlah_pendapatan == 0:
        st.info("Sila masukkan anggaran pendapatan tahunan anda di atas untuk memulakan pengiraan.")
    elif wajib_zakat:
        st.success(
            f"**WAJIB ZAKAT** — Baki layak zakat (**RM {pendapatan_berzakat:,.2f}**) "
            f"menyamai atau melebihi nisab semasa (**RM {nisab:,.2f}**)."
        )

        c1, c2 = st.columns(2)
        c1.metric("Zakat Tahunan (2.5%)", f"RM {jumlah_zakat_tahun:,.2f}")
        c2.metric("Anggaran Potongan Bulanan", f"RM {jumlah_zakat_bulan:,.2f}")

        st.link_button(
            "Bayar Secara Dalam Talian (Portal FPX LZS)",
            "https://fpx.zakatselangor.com.my/",
            use_container_width=True,
        )
    else:
        st.info(
            f"**TIDAK WAJIB ZAKAT** — Baki layak zakat (**RM {pendapatan_berzakat:,.2f}**) "
            f"kurang daripada nisab semasa (**RM {nisab:,.2f}**)."
        )


if __name__ == "__main__":
    main()